package com.example.assistant.auth;

import com.example.assistant.config.SecurityProperties;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import jakarta.annotation.PostConstruct;

@Service
public class AuthService {
    private final SecurityProperties securityProperties;
    private final PasswordEncoder passwordEncoder;
    private String encodedPassword;

    public AuthService(SecurityProperties securityProperties, PasswordEncoder passwordEncoder) {
        this.securityProperties = securityProperties;
        this.passwordEncoder = passwordEncoder;
    }

    @PostConstruct
    public void initPassword() {
        this.encodedPassword = passwordEncoder.encode(securityProperties.getDemoPassword());
    }

    public boolean authenticate(String username, String rawPassword) {
        return securityProperties.getDemoUsername().equals(username)
                && passwordEncoder.matches(rawPassword, encodedPassword);
    }
}
