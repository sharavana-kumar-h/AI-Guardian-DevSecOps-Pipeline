package com.example.devsecops.repository;

import com.example.devsecops.model.CalculationRecord;
import org.springframework.data.jpa.repository.JpaRepository;

public interface CalculationRepository extends JpaRepository<CalculationRecord, Long> {
}
