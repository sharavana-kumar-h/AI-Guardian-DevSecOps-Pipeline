package com.example.devsecops.controller;

import com.example.devsecops.model.CalculationRecord;
import com.example.devsecops.repository.CalculationRepository;
import com.example.devsecops.service.CalculatorService;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

@RestController
@RequestMapping("/api/calculator")
public class CalculatorController {
    private final CalculatorService calculatorService;
    private final CalculationRepository calculationRepository;

    public CalculatorController(CalculatorService calculatorService, CalculationRepository calculationRepository) {
        this.calculatorService = calculatorService;
        this.calculationRepository = calculationRepository;
    }

    @PostMapping
    public ResponseEntity<CalculationResponse> calculate(@Valid @RequestBody CalculationRequest request) {
        double result = calculatorService.calculate(request.operation(), request.a(), request.b());
        String expression = "%s(%s,%s)".formatted(request.operation(), request.a(), request.b());
        CalculationRecord saved = calculationRepository.save(new CalculationRecord(expression, result));
        return ResponseEntity.ok(new CalculationResponse(saved.getId(), expression, result));
    }

    @GetMapping("/history")
    public ResponseEntity<List<CalculationRecord>> history() {
        return ResponseEntity.ok(calculationRepository.findAll());
    }

    public record CalculationRequest(
            @NotBlank String operation,
            @NotNull Double a,
            @NotNull Double b
    ) {}

    public record CalculationResponse(Long id, String expression, Double result) {}
}
