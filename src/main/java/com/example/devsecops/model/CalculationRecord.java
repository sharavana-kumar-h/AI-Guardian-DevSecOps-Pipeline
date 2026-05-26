package com.example.devsecops.model;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import jakarta.validation.constraints.NotBlank;

import java.time.Instant;

@Entity
@Table(name = "calculation_records")
public class CalculationRecord {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @NotBlank
    @Column(nullable = false)
    private String expression;

    @Column(nullable = false)
    private Double result;

    @Column(nullable = false)
    private Instant createdAt = Instant.now();

    protected CalculationRecord() {
    }

    public CalculationRecord(String expression, Double result) {
        this.expression = expression;
        this.result = result;
    }

    public Long getId() {
        return id;
    }

    public String getExpression() {
        return expression;
    }

    public Double getResult() {
        return result;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }
}
