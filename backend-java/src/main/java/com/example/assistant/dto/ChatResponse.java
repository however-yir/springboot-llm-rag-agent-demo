package com.example.assistant.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

import java.util.List;

public record ChatResponse(
        @JsonProperty("session_id") String sessionId,
        String answer,
        List<AgentStep> trace,
        @JsonProperty("retrieval_preview") List<SearchHit> retrievalPreview
) {
}
