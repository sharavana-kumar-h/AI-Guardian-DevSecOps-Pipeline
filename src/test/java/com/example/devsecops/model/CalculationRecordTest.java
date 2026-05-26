package com.example.devsecops.model;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;

class CalculationRecordTest {
    @Test
    void createsCalculationRecordWithTimestamp() {
        CalculationRecord record = new CalculationRecord("add(2.0,3.0)", 5.0);

        assertNull(record.getId());
        assertEquals("add(2.0,3.0)", record.getExpression());
        assertEquals(5.0, record.getResult());
        assertNotNull(record.getCreatedAt());
    }
}
