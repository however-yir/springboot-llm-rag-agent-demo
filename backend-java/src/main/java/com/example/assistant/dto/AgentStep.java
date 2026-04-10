package com.example.assistant.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.Map;

public record AgentStep(
        Integer step,
        String thought,
        String action,
        @JsonProperty("action_input")
        Map<String, Object> actionInput,
        Object observation
) {
}
