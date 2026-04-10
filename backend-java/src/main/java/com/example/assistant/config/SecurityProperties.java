package com.example.assistant.config;

import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "app.security")
public class SecurityProperties {
    private String jwtSecret = "replace-with-at-least-32-characters-secret-key";
    private long jwtExpiresSeconds = 7200;
    private String demoUsername = "admin";
    private String demoPassword = "admin123456";

    public String getJwtSecret() {
        return jwtSecret;
    }

    public void setJwtSecret(String jwtSecret) {
        this.jwtSecret = jwtSecret;
    }

    public long getJwtExpiresSeconds() {
        return jwtExpiresSeconds;
    }

    public void setJwtExpiresSeconds(long jwtExpiresSeconds) {
        this.jwtExpiresSeconds = jwtExpiresSeconds;
    }

    public String getDemoUsername() {
        return demoUsername;
    }

    public void setDemoUsername(String demoUsername) {
        this.demoUsername = demoUsername;
    }

    public String getDemoPassword() {
        return demoPassword;
    }

    public void setDemoPassword(String demoPassword) {
        this.demoPassword = demoPassword;
    }
}
