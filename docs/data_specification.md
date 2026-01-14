# Synthetic Data Specification

## Overview
This document describes the synthetic crowd behavior datasets generated for the Intelligent Crowd Monitoring System project.

## Dataset Structure

### File Format
- **Format:** CSV (Comma-Separated Values)
- **Encoding:** UTF-8
- **Location:** `data/synthetic/`

### Column Specifications

| Column | Type | Range | Description |
|--------|------|-------|-------------|
| timestamp | Integer | 0 to duration | Time step in simulation |
| zone_id | String | Zone_X_Y | Unique zone identifier (X: row, Y: col) |
| x_coord | Integer | 0-9 | Row position in 10x10 grid |
| y_coord | Integer | 0-9 | Column position in 10x10 grid |
| density | Float | 0-10 | People per square meter |
| people_count | Integer | 0-100 | Actual number of people (density × 10m²) |
| movement_speed | Float | 0-3 | Movement speed in m/s |
| direction_variance | Float | 0-180 | Movement direction chaos (degrees) |

## Scenario Descriptions

### 1. Normal Scenario
**File:** `normal_scenario.csv`
- **Duration:** 200 timesteps
- **Records:** 20,000 (100 zones × 200 timesteps)
- **Density Range:** 0.5 - 2.5 people/m²
- **Characteristics:**
  - Low to moderate crowd density
  - Regular movement patterns (0.8-1.5 m/s)
  - Low direction variance (20-60°)
  - ~90% zones classified as "Safe"
- **Use Case:** Baseline normal operations

### 2. Rush Hour Scenario
**File:** `rush_hour_scenario.csv`
- **Duration:** 200 timesteps
- **Records:** 20,000
- **Density Range:** 2.0 - 5.0 people/m²
- **Characteristics:**
  - Moderate to high density
  - High-traffic zones at entrances and center
  - Varied movement (0.5-1.3 m/s)
  - Moderate direction variance (40-100°)
  - Mix of Safe, Moderate, and Warning zones
- **Use Case:** Peak hours, busy periods

### 3. Emergency Scenario
**File:** `emergency_scenario.csv`
- **Duration:** 150 timesteps
- **Records:** 15,000
- **Density Range:** 4.0 - 7.5 people/m²
- **Characteristics:**
  - High density throughout
  - Emergency begins at timestep 30
  - Very slow movement (0.2-0.8 m/s) due to panic
  High direction variance (100-180°) indicating chaos
Multiple Critical and Emergency zones
Density concentrated near exits
Use Case: Emergency evacuation, panic situations

### 4. Event End Scenario
File: `event_end_scenario.csv`

**Duration:**  250 timesteps
**Records:** 25,000
**Density Range:** 1.0 - 6.0 people/m²
**Characteristics:**

- Gradually increasing density over time
- Simulates venue evacuation after event
- Density builds near exit points
- Speed decreases as density increases
- Transitions from Safe → Warning → Critical


**Use Case:** Post-event crowd dispersal