package com.example.assistant.controller;

import com.example.assistant.auth.AuthService;
import com.example.assistant.config.SecurityProperties;
import com.example.assistant.dto.AuthLoginRequest;
import com.example.assistant.dto.AuthLoginResponse;
import com.example.assistant.security.JwtService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

@RestController
@RequestMapping(path = "/api/v1/auth", produces = MediaType.APPLICATION_JSON_VALUE)
public class AuthController {
    private final AuthService authService;
    private final JwtService jwtService;
    private final SecurityProperties securityProperties;

    public AuthController(AuthService authService, JwtService jwtService, SecurityProperties securityProperties) {
        this.authService = authService;
        this.jwtService = jwtService;
        this.securityProperties = securityProperties;
    }

    @PostMapping("/login")
    public AuthLoginResponse login(@RequestBody @Valid AuthLoginRequest request) {
        boolean ok = authService.authenticate(request.username(), request.password());
        if (!ok) {
            throw new ResponseStatusException(HttpStatus.UNAUTHORIZED, "Invalid username or password");
        }

        String token = jwtService.generateToken(request.username());
        return new AuthLoginResponse(token, "Bearer", securityProperties.getJwtExpiresSeconds());
    }
}
