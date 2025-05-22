package com.vitalpaw.mainclient.service;

import com.vitalpaw.mainclient.model.User;
import com.vitalpaw.mainclient.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.RedisTemplate;
import org.springframework.mail.SimpleMailMessage;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.stereotype.Service;

import java.security.SecureRandom;
import java.util.Base64;
import java.util.concurrent.TimeUnit;

@Service
public class UserService {
    @Autowired
    private UserRepository userRepository;
    @Autowired
    private JavaMailSender mailSender;
    @Autowired
    private BCryptPasswordEncoder passwordEncoder;
    @Autowired
    private RedisTemplate<String, String> redisTemplate;

    public void registerUser(String email, String firstName, String password, String lastName, String phone, String city) {
        if (userRepository.findByEmail(email) != null) {
            throw new IllegalArgumentException("El correo ya está registrado");
        }

        User user = new User();
        user.setEmail(email);
        user.setFirstName(firstName);
        user.setLastName(lastName);
        user.setPhone(phone);
        user.setCity(city);
        user.setPassword(passwordEncoder.encode(password));
        user.setUsername(generateUniqueUsername(email));
        user.setVerificationToken(generateVerificationToken());
        user.setVerified(false);
        userRepository.save(user);
        sendVerificationEmail(email, user.getVerificationToken());
    }

    public boolean verifyUser(String email, String token) {
        User user = userRepository.findByEmail(email);
        if (user != null && token.equals(user.getVerificationToken())) {
            user.setVerified(true);
            user.setVerificationToken(null);
            userRepository.save(user);
            return true;
        }
        return false;
    }

    public void requestPasswordReset(String email) {
        User user = userRepository.findByEmail(email);
        if (user != null) {
            String token = generateVerificationToken();
            redisTemplate.opsForValue().set("reset_token:" + email, token, 1, TimeUnit.HOURS);
            sendPasswordResetEmail(email, token);
        }
    }

    public boolean confirmPasswordReset(String email, String token, String newPassword) {
        String storedToken = redisTemplate.opsForValue().get("reset_token:" + email);
        if (token.equals(storedToken)) {
            User user = userRepository.findByEmail(email);
            if (user != null) {
                user.setPassword(passwordEncoder.encode(newPassword));
                userRepository.save(user);
                redisTemplate.delete("reset_token:" + email);
                return true;
            }
        }
        return false;
    }

    public void updateDeviceToken(String userId, String token) {
        redisTemplate.opsForValue().set("device_token:" + userId, token, 30, TimeUnit.DAYS);
    }

    private String generateUniqueUsername(String email) {
        String baseUsername = email.split("@")[0].substring(0, Math.min(30, email.split("@")[0].length()));
        String username = baseUsername;
        int counter = 1;
        while (userRepository.findByUsername(username) != null) {
            username = baseUsername + counter;
            counter++;
        }
        return username;
    }

    private String generateVerificationToken() {
        SecureRandom random = new SecureRandom();
        byte[] bytes = new byte[40];
        random.nextBytes(bytes);
        return Base64.getUrlEncoder().withoutPadding().encodeToString(bytes);
    }

    private void sendVerificationEmail(String email, String token) {
        SimpleMailMessage message = new SimpleMailMessage();
        message.setTo(email);
        message.setSubject("Verifica tu correo - VitalPaw");
        message.setText("Por favor, verifica tu correo haciendo clic en: http://api.vitalpaw.com/api/users/verify?email=" + email + "&token=" + token);
        mailSender.send(message);
    }

    private void sendPasswordResetEmail(String email, String token) {
        SimpleMailMessage message = new SimpleMailMessage();
        message.setTo(email);
        message.setSubject("Recuperación de Contraseña");
        message.setText("Usa este token para restablecer tu contraseña: " + token);
        mailSender.send(message);
    }
}