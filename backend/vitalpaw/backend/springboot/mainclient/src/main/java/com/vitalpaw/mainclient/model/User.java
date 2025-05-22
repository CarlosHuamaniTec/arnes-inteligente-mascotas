package com.vitalpaw.mainclient.model;

import jakarta.persistence.*;
import lombok.Data;

@Entity
@Table(name = "users")
@Data
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(unique = true, nullable = false)
    private String email;

    @Column(nullable = false)
    private String password;

    @Column(nullable = false)
    private String firstName;

    @Column
    private String lastName;

    @Column
    private String phone;

    @Column
    private String city;

    @Column(unique = true)
    private String username;

    @Column
    private String verificationToken;

    @Column
    private boolean isVerified;
}