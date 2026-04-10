package com.example.assistant.dto;

import java.util.Map;

public record SearchHit(
        String content,
        Map<String, Object> metadata
) {
}
