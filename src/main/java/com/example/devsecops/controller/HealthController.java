package com.example.devsecops.controller;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.time.Instant;
import java.util.Map;

@RestController
public class HealthController {
    @GetMapping("/")
    public Map<String, Object> index() {
        return Map.of(
                "service", "ai-devsecops-demo",
                "status", "running",
                "timestamp", Instant.now().toString()
        );
    }
}
