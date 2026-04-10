package com.example.assistant.security;

import com.example.assistant.config.SecurityProperties;
import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import org.springframework.stereotype.Service;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.util.Arrays;
import java.util.Date;

@Service
public class JwtService {
    private final SecurityProperties securityProperties;

    public JwtService(SecurityProperties securityProperties) {
        this.securityProperties = securityProperties;
    }

    public String generateToken(String username) {
        Instant now = Instant.now();
        Instant expireAt = now.plusSeconds(securityProperties.getJwtExpiresSeconds());

        return Jwts.builder()
                .subject(username)
                .issuedAt(Date.from(now))
                .expiration(Date.from(expireAt))
                .signWith(signingKey())
                .compact();
    }

    public String extractUsername(String token) {
        return parseClaims(token).getSubject();
    }

    public boolean isTokenValid(String token) {
        Date expiration = parseClaims(token).getExpiration();
        return expiration.after(new Date());
    }

    private Claims parseClaims(String token) {
        return Jwts.parser()
                .verifyWith(signingKey())
                .build()
                .parseSignedClaims(token)
                .getPayload();
    }

    private SecretKey signingKey() {
        byte[] rawBytes = securityProperties.getJwtSecret().getBytes(StandardCharsets.UTF_8);
        byte[] normalized = Arrays.copyOf(rawBytes, 32);
        return Keys.hmacShaKeyFor(normalized);
    }
}
