package com.example.devsecops.controller;

import com.example.devsecops.model.CalculationRecord;
import com.example.devsecops.repository.CalculationRepository;
import com.example.devsecops.service.CalculatorService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.validation.beanvalidation.LocalValidatorFactoryBean;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;

import java.util.List;

import static org.hamcrest.Matchers.hasSize;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@ExtendWith(MockitoExtension.class)
class CalculatorControllerTest {
    @Mock
    private CalculatorService calculatorService;

    @Mock
    private CalculationRepository calculationRepository;

    private MockMvc mockMvc;

    @BeforeEach
    void setUp() {
        CalculatorController controller = new CalculatorController(calculatorService, calculationRepository);
        LocalValidatorFactoryBean validator = new LocalValidatorFactoryBean();
        validator.afterPropertiesSet();
        mockMvc = MockMvcBuilders.standaloneSetup(controller)
                .setValidator(validator)
                .build();
    }

    @Test
    void calculatesAndStoresResult() throws Exception {
        when(calculatorService.calculate("add", 10.0, 5.0)).thenReturn(15.0);
        when(calculationRepository.save(any(CalculationRecord.class)))
                .thenReturn(new CalculationRecord("add(10.0,5.0)", 15.0));

        mockMvc.perform(post("/api/calculator")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {"operation":"add","a":10,"b":5}
                                """))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.expression").value("add(10.0,5.0)"))
                .andExpect(jsonPath("$.result").value(15.0));

        verify(calculatorService).calculate("add", 10.0, 5.0);
        verify(calculationRepository).save(any(CalculationRecord.class));
    }

    @Test
    void rejectsInvalidRequestBody() throws Exception {
        mockMvc.perform(post("/api/calculator")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("""
                                {"operation":"","a":10}
                                """))
                .andExpect(status().isBadRequest());
    }

    @Test
    void returnsCalculationHistory() throws Exception {
        when(calculationRepository.findAll()).thenReturn(List.of(
                new CalculationRecord("add(1.0,2.0)", 3.0),
                new CalculationRecord("multiply(3.0,4.0)", 12.0)
        ));

        mockMvc.perform(get("/api/calculator/history"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(2)))
                .andExpect(jsonPath("$[0].expression").value("add(1.0,2.0)"))
                .andExpect(jsonPath("$[1].result").value(12.0));
    }
}
