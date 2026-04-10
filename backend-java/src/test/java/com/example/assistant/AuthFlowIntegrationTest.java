package com.example.assistant;

import com.example.assistant.dto.ToolDescriptor;
import com.example.assistant.service.AiGatewayService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.context.TestPropertySource;
import org.springframework.test.web.servlet.MockMvc;

import java.util.List;

import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@AutoConfigureMockMvc
@TestPropertySource(properties = {
        "app.security.demo-username=admin",
        "app.security.demo-password=admin123456",
        "app.security.jwt-secret=01234567890123456789012345678901"
})
class AuthFlowIntegrationTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private AiGatewayService aiGatewayService;

    @Test
    void loginAndAccessProtectedApi() throws Exception {
        when(aiGatewayService.tools()).thenReturn(List.of(
                new ToolDescriptor("get_course_schedule", "desc", List.of("student_id", "week"))
        ));

        String loginPayload = "{" +
                "\"username\":\"admin\"," +
                "\"password\":\"admin123456\"" +
                "}";

        String tokenResponse = mockMvc.perform(post("/api/v1/auth/login")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(loginPayload))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.access_token").exists())
                .andReturn()
                .getResponse()
                .getContentAsString();

        String token = tokenResponse.split("\"access_token\":\"")[1].split("\"")[0];

        mockMvc.perform(get("/api/v1/tools")
                        .header("Authorization", "Bearer " + token))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].name").value("get_course_schedule"));
    }

    @Test
    void shouldRejectProtectedApiWithoutJwt() throws Exception {
        mockMvc.perform(get("/api/v1/tools"))
                .andExpect(status().isUnauthorized());
    }
}
