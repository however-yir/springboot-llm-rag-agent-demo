package com.example.assistant.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

public record AuthLoginResponse(
        @JsonProperty("access_token") String accessToken,
        @JsonProperty("token_type") String tokenType,
        @JsonProperty("expires_in") long expiresIn
) {
}
