package com.example.assistant.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.List;

public record ToolDescriptor(
        String name,
        String description,
        @JsonProperty("required_params") List<String> requiredParams
) {
}
