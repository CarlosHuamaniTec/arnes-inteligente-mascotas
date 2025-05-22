package com.vitalpaw.mainclient.model;

import lombok.Data;

@Data
public class BiometricData {
    private String petId;
    private int heartRate;
    private double temperature;
    private String movement;
}