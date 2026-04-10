package com.example.assistant.dto;

import java.util.List;

public record SearchResponse(
        String query,
        List<SearchHit> hits
) {
}
