package com.example.assistant.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;

public record SearchRequest(
        @NotBlank String query,
        @JsonProperty("top_k") @Min(1) Integer topK,
        String department
) {
}
