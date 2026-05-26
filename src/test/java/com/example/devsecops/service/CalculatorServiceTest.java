package com.example.devsecops.service;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.CsvSource;
import org.junit.jupiter.params.provider.NullAndEmptySource;
import org.junit.jupiter.params.provider.ValueSource;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

class CalculatorServiceTest {
    private final CalculatorService service = new CalculatorService();

    @Nested
    @DisplayName("happy path calculations")
    class HappyPathCalculations {
        @ParameterizedTest(name = "{0}({1}, {2}) = {3}")
        @CsvSource({
                "add, 3, 4, 7",
                "subtract, 6, 4, 2",
                "multiply, 3, 4, 12",
                "divide, 5, 2, 2.5",
                "add, -3, 4, 1",
                "subtract, -3, -4, 1",
                "multiply, -3, 4, -12",
                "divide, -9, 3, -3"
        })
        void calculatesSupportedOperations(String operation, double a, double b, double expected) {
            assertEquals(expected, service.calculate(operation, a, b), 0.000001);
        }

        @ParameterizedTest
        @ValueSource(strings = {"ADD", " Add ", "aDd"})
        void normalizesOperationCaseAndWhitespace(String operation) {
            assertEquals(7.0, service.calculate(operation, 3, 4), 0.000001);
        }
    }

    @Nested
    @DisplayName("defensive validation")
    class DefensiveValidation {
        @Test
        void blocksDivisionByZero() {
            IllegalArgumentException exception = assertThrows(
                    IllegalArgumentException.class,
                    () -> service.calculate("divide", 10, 0)
            );
            assertEquals("Division by zero is not allowed", exception.getMessage());
        }

        @Test
        void rejectsUnsupportedOperation() {
            IllegalArgumentException exception = assertThrows(
                    IllegalArgumentException.class,
                    () -> service.calculate("mod", 10, 3)
            );
            assertEquals("Unsupported operation: mod", exception.getMessage());
        }

        @ParameterizedTest
        @NullAndEmptySource
        @ValueSource(strings = {"   ", "\t"})
        void rejectsMissingOperation(String operation) {
            IllegalArgumentException exception = assertThrows(
                    IllegalArgumentException.class,
                    () -> service.calculate(operation, 10, 3)
            );
            assertEquals("Operation is required", exception.getMessage());
        }
    }
}
