package com.example.assistant.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.NotBlank;

public record ChatRequest(
        @JsonProperty("user_id") String userId,
        @JsonProperty("session_id") String sessionId,
        @NotBlank String message,
        String department
) {
}
