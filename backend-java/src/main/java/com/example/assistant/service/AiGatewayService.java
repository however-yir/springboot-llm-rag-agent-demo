package com.example.assistant.service;

import com.example.assistant.dto.ChatRequest;
import com.example.assistant.dto.ChatResponse;
import com.example.assistant.dto.SearchRequest;
import com.example.assistant.dto.SearchResponse;
import com.example.assistant.dto.ToolDescriptor;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Flux;

import java.time.Duration;
import java.util.List;

@Service
public class AiGatewayService {
    private final WebClient aiServiceWebClient;

    public AiGatewayService(WebClient aiServiceWebClient) {
        this.aiServiceWebClient = aiServiceWebClient;
    }

    public ChatResponse chat(ChatRequest request) {
        return aiServiceWebClient.post()
                .uri("/api/v1/agent/chat")
                .contentType(MediaType.APPLICATION_JSON)
                .bodyValue(request)
                .retrieve()
                .bodyToMono(ChatResponse.class)
                .timeout(Duration.ofSeconds(90))
                .block();
    }

    public Flux<String> chatStream(ChatRequest request) {
        return aiServiceWebClient.post()
                .uri("/api/v1/agent/chat/stream")
                .contentType(MediaType.APPLICATION_JSON)
                .accept(MediaType.TEXT_EVENT_STREAM)
                .bodyValue(request)
                .retrieve()
                .bodyToFlux(String.class)
                .timeout(Duration.ofSeconds(120))
                .onErrorResume(ex -> Flux.just("event: error\ndata: {\"message\":\"stream unavailable\"}\n\n"));
    }

    public SearchResponse search(SearchRequest request) {
        return aiServiceWebClient.post()
                .uri("/api/v1/rag/search")
                .contentType(MediaType.APPLICATION_JSON)
                .bodyValue(request)
                .retrieve()
                .bodyToMono(SearchResponse.class)
                .timeout(Duration.ofSeconds(30))
                .block();
    }

    public List<ToolDescriptor> tools() {
        return aiServiceWebClient.get()
                .uri("/api/v1/tools")
                .retrieve()
                .bodyToFlux(ToolDescriptor.class)
                .collectList()
                .timeout(Duration.ofSeconds(30))
                .block();
    }
}
