package com.example.devsecops.controller;

import org.junit.jupiter.api.Test;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

class HealthControllerTest {
    private final MockMvc mockMvc = MockMvcBuilders.standaloneSetup(new HealthController()).build();

    @Test
    void returnsLandingHealthPayload() throws Exception {
        mockMvc.perform(get("/"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.service").value("ai-devsecops-demo"))
                .andExpect(jsonPath("$.status").value("running"))
                .andExpect(jsonPath("$.timestamp").exists());
    }
}
