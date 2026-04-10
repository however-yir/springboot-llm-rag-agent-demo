package com.example.assistant.session;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Component;

import java.time.Duration;
import java.util.ArrayDeque;
import java.util.Deque;
import java.util.List;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Component
public class SessionStore {
    private static final Logger log = LoggerFactory.getLogger(SessionStore.class);
    private static final int MAX_MESSAGES = 10;

    private final StringRedisTemplate redisTemplate;
    private final ObjectMapper objectMapper;
    private final long ttlSeconds;
    private final Map<String, Deque<String>> fallbackHistories = new ConcurrentHashMap<>();

    public SessionStore(
            StringRedisTemplate redisTemplate,
            ObjectMapper objectMapper,
            @Value("${app.session.ttl-seconds:86400}") long ttlSeconds
    ) {
        this.redisTemplate = redisTemplate;
        this.objectMapper = objectMapper;
        this.ttlSeconds = ttlSeconds;
    }

    public void append(String sessionId, String role, String content) {
        String value;
        try {
            value = objectMapper.writeValueAsString(Map.of("role", role, "content", content));
        } catch (JsonProcessingException ex) {
            value = role + ": " + content;
        }

        String redisKey = redisKey(sessionId);
        try {
            redisTemplate.opsForList().rightPush(redisKey, value);
            redisTemplate.opsForList().trim(redisKey, -MAX_MESSAGES, -1);
            redisTemplate.expire(redisKey, Duration.ofSeconds(ttlSeconds));
        } catch (Exception ex) {
            log.warn("Redis unavailable, falling back to in-memory session cache: {}", ex.getMessage());
            appendFallback(sessionId, value);
        }
    }

    public List<String> recent(String sessionId) {
        String redisKey = redisKey(sessionId);
        try {
            List<String> values = redisTemplate.opsForList().range(redisKey, 0, -1);
            if (values != null) {
                return values;
            }
        } catch (Exception ex) {
            log.warn("Failed to fetch session history from Redis, using fallback: {}", ex.getMessage());
        }

        Deque<String> deque = fallbackHistories.getOrDefault(sessionId, new ArrayDeque<>());
        return deque.stream().toList();
    }

    private void appendFallback(String sessionId, String value) {
        fallbackHistories.computeIfAbsent(sessionId, k -> new ArrayDeque<>());
        Deque<String> deque = fallbackHistories.get(sessionId);
        deque.addLast(value);
        if (deque.size() > MAX_MESSAGES) {
            deque.removeFirst();
        }
    }

    private String redisKey(String sessionId) {
        return "session:" + sessionId + ":messages";
    }
}
