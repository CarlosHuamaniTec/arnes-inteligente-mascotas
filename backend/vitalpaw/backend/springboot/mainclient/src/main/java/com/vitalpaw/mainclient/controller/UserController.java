package com.vitalpaw.mainclient.controller;

import com.vitalpaw.mainclient.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/users")
public class UserController {
    @Autowired
    private UserService userService;

    @PostMapping("/register")
    public ResponseEntity<?> register(@RequestBody Map<String, String> request) {
        String email = request.get("email");
        String firstName = request.get("first_name");
        String password = request.get("password");
        String lastName = request.get("last_name");
        String phone = request.get("phone");
        String city = request.get("city");
        try {
            userService.registerUser(email, firstName, password, lastName, phone, city);
            return ResponseEntity.ok("Usuario registrado. Verifica tu correo.");
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().body(e.getMessage());
        }
    }

    @GetMapping("/verify")
    public ResponseEntity<?> verify(@RequestParam String email, @RequestParam String token) {
        boolean success = userService.verifyUser(email, token);
        if (success) {
            return ResponseEntity.ok("Correo verificado");
        }
        return ResponseEntity.badRequest().body("Token inválido");
    }

    @PostMapping("/password-reset")
    public ResponseEntity<?> resetPassword(@RequestBody Map<String, String> request) {
        String email = request.get("email");
        userService.requestPasswordReset(email);
        return ResponseEntity.ok("Correo de recuperación enviado");
    }

    @PostMapping("/password-confirm")
    public ResponseEntity<?> confirmPassword(@RequestBody Map<String, String> request) {
        String email = request.get("email");
        String token = request.get("token");
        String newPassword = request.get("new_password");
        boolean success = userService.confirmPasswordReset(email, token, newPassword);
        if (success) {
            return ResponseEntity.ok("Contraseña actualizada");
        }
        return ResponseEntity.badRequest().body("Token inválido");
    }

    @PostMapping("/device-token")
    public ResponseEntity<?> updateDeviceToken(@RequestBody Map<String, String> request) {
        String token = request.get("device_token");
        String userId = request.get("user_id");
        userService.updateDeviceToken(userId, token);
        return ResponseEntity.ok("Token actualizado");
    }
}