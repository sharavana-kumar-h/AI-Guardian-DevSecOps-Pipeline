package com.example.devsecops.service;

import org.springframework.stereotype.Service;

import java.util.Locale;

@Service
public class CalculatorService {
    public double calculate(String operation, double a, double b) {
        String normalizedOperation = normalizeOperation(operation);

        return switch (normalizedOperation) {
            case "add" -> a + b;
            case "subtract" -> a - b;
            case "multiply" -> a * b;
            case "divide" -> divide(a, b);
            default -> throw new IllegalArgumentException("Unsupported operation: " + operation);
        };
    }

    private String normalizeOperation(String operation) {
        if (operation == null || operation.isBlank()) {
            throw new IllegalArgumentException("Operation is required");
        }
        return operation.trim().toLowerCase(Locale.ROOT);
    }

    private double divide(double a, double b) {
        if (b == 0) {
            throw new IllegalArgumentException("Division by zero is not allowed");
        }
        return a / b;
    }
}
