package com.vitalpaw.mainclient.model;

import lombok.Data;

@Data
public class Thresholds {
    private String breed;
    private double minHeartRate;
    private double maxHeartRate;
    private double minTemperature;
    private double maxTemperature;

    public Thresholds(String breed, double minHeartRate, double maxHeartRate, double minTemperature, double maxTemperature) {
        this.breed = breed;
        this.minHeartRate = minHeartRate;
        this.maxHeartRate = maxHeartRate;
        this.minTemperature = minTemperature;
        this.maxTemperature = maxTemperature;
    }
}