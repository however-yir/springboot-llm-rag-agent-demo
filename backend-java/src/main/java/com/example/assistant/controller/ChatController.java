package com.example.assistant.controller;

import com.example.assistant.dto.ChatRequest;
import com.example.assistant.dto.ChatResponse;
import com.example.assistant.dto.SearchRequest;
import com.example.assistant.dto.SearchResponse;
import com.example.assistant.dto.ToolDescriptor;
import com.example.assistant.service.AiGatewayService;
import com.example.assistant.session.SessionStore;
import jakarta.validation.Valid;
import org.springframework.http.MediaType;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import reactor.core.publisher.Flux;

import java.util.List;

@RestController
@Validated
@RequestMapping(path = "/api/v1")
public class ChatController {
    private final AiGatewayService aiGatewayService;
    private final SessionStore sessionStore;

    public ChatController(AiGatewayService aiGatewayService, SessionStore sessionStore) {
        this.aiGatewayService = aiGatewayService;
        this.sessionStore = sessionStore;
    }

    @PostMapping(path = "/chat", produces = MediaType.APPLICATION_JSON_VALUE)
    public ChatResponse chat(@RequestBody @Valid ChatRequest request) {
        String sessionId = request.sessionId() == null ? "session-java-001" : request.sessionId();
        String userId = request.userId() == null ? "java-user" : request.userId();

        ChatRequest normalized = new ChatRequest(userId, sessionId, request.message(), request.department());
        sessionStore.append(sessionId, "user", request.message());
        ChatResponse response = aiGatewayService.chat(normalized);
        sessionStore.append(sessionId, "assistant", response.answer());
        return response;
    }

    @PostMapping(path = "/chat/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<String> chatStream(@RequestBody @Valid ChatRequest request) {
        String sessionId = request.sessionId() == null ? "session-java-001" : request.sessionId();
        String userId = request.userId() == null ? "java-user" : request.userId();
        ChatRequest normalized = new ChatRequest(userId, sessionId, request.message(), request.department());
        sessionStore.append(sessionId, "user", request.message());
        return aiGatewayService.chatStream(normalized)
                .doOnNext(chunk -> {
                    if (chunk.contains("event: done") || chunk.contains("event: error")) {
                        sessionStore.append(sessionId, "assistant", "[stream completed]");
                    }
                });
    }

    @PostMapping(path = "/rag/search", produces = MediaType.APPLICATION_JSON_VALUE)
    public SearchResponse ragSearch(@RequestBody @Valid SearchRequest request) {
        Integer topK = request.topK() == null ? 4 : request.topK();
        SearchRequest normalized = new SearchRequest(request.query(), topK, request.department());
        return aiGatewayService.search(normalized);
    }

    @GetMapping(path = "/tools", produces = MediaType.APPLICATION_JSON_VALUE)
    public List<ToolDescriptor> tools() {
        return aiGatewayService.tools();
    }

    @GetMapping(path = "/sessions/recent", produces = MediaType.APPLICATION_JSON_VALUE)
    public List<String> recent(@RequestParam(name = "session_id", required = false) String sessionId) {
        String normalized = sessionId == null ? "session-java-001" : sessionId;
        return sessionStore.recent(normalized);
    }
}
