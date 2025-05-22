package com.vitalpaw.mainclient.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.firebase.messaging.FirebaseMessaging;
import com.google.firebase.messaging.Message;
import com.google.firebase.messaging.Notification;
import com.vitalpaw.mainclient.config.MqttConfig;
import com.vitalpaw.mainclient.model.BiometricData;
import com.vitalpaw.mainclient.model.Pet;
import com.vitalpaw.mainclient.model.Thresholds;
import com.vitalpaw.mainclient.repository.PetRepository;
import org.eclipse.paho.client.mqttv3.*;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.http.ResponseEntity;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.ArrayList;
import java.util.List;

@Service
public class MqttService {
    private final MqttAsyncClient client;
    private final ObjectMapper objectMapper;
    private final FirebaseMessaging firebaseMessaging;
    private final RedisTemplate<String, String> redisTemplate;
    private final PetRepository petRepository;
    private final RestTemplate restTemplate;
    
    public MqttService(ObjectMapper objectMapper, FirebaseMessaging firebaseMessaging, RedisTemplate<String, String> redisTemplate, PetRepository petRepository, MqttConfig mqttConfig) throws MqttException {
        this.objectMapper = objectMapper;
        this.firebaseMessaging = firebaseMessaging;
        this.redisTemplate = redisTemplate;
        this.petRepository = petRepository;
        this.restTemplate = new RestTemplate();
        this.client = new MqttAsyncClient(mqttConfig.getBroker(), "mainclient");
        client.setCallback(new MqttCallback() {
            @Override
            public void messageArrived(String topic, MqttMessage message) throws Exception {
                redisTemplate.opsForList().leftPush("biometric_queue", new String(message.getPayload()));
            }
            public void connectionLost(Throwable cause) {}
            public void deliveryComplete(IMqttDeliveryToken token) {}
        });
        MqttConnectOptions options = new MqttConnectOptions();
        options.setUserName(mqttConfig.getUsername());
        options.setPassword(mqttConfig.getPassword().toCharArray());
        client.connect(options).waitForCompletion();
        client.subscribe("pet/biometric/+", 1);
    }

    @Scheduled(fixedRate = 100)
    public void processBiometricQueue() throws Exception {
        String payload = redisTemplate.opsForList().rightPop("biometric_queue");
        while (payload != null) {
            BiometricData data = objectMapper.readValue(payload, BiometricData.class);
            String breed = getPetBreed(data.getPetId());
            Thresholds thresholds = getThresholds(breed);
            List<String> alerts = checkThresholds(data, thresholds);
            if (!alerts.isEmpty()) {
                sendNotification(data.getPetId(), alerts);
            }
            payload = redisTemplate.opsForList().rightPop("biometric_queue");
        }
    }

    private String getPetBreed(String petId) {
        Pet pet = petRepository.findById(Long.parseLong(petId)).orElse(null);
        return pet != null ? pet.getBreed() : "Labrador";
    }

    private Thresholds getThresholds(String breed) {
        try {
            ResponseEntity<Thresholds> response = restTemplate.getForEntity(
                "http://django:8000/api/thresholds/?breed=" + breed,
                Thresholds.class
            );
            return response.getBody();
        } catch (Exception e) {
            return new Thresholds(breed, 60.0, 120.0, 36.5, 39.5);
        }
    }

    private List<String> checkThresholds(BiometricData data, Thresholds thresholds) {
        List<String> alerts = new ArrayList<>();
        if (data.getHeartRate() < thresholds.getMinHeartRate() || data.getHeartRate() > thresholds.getMaxHeartRate()) {
            alerts.add("Frecuencia cardíaca anormal: " + data.getHeartRate());
        }
        if (data.getTemperature() < thresholds.getMinTemperature() || data.getTemperature() > thresholds.getMaxTemperature()) {
            alerts.add("Temperatura anormal: " + data.getTemperature());
        }
        return alerts;
    }

    private void sendNotification(String petId, List<String> alerts) {
        String deviceToken = redisTemplate.opsForValue().get("device_token:" + petId);
        if (deviceToken != null) {
            Message message = Message.builder()
                .setNotification(Notification.builder()
                    .setTitle("Alerta de Salud")
                    .setBody(String.join(", ", alerts))
                    .build())
                .setToken(deviceToken)
                .build();
            try {
                firebaseMessaging.send(message);
            } catch (Exception e) {
                // Log error
            }
        }
    }
}