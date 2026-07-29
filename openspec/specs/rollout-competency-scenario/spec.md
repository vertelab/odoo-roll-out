# rollout-competency-scenario Specification

## Purpose

Group competency strategies into scenario packages for comparison. Evaluate total cost, lead time, risk level, and earliest completion date across alternative competency fulfillment approaches.

## ADDED Requirements

### Requirement: Create competency scenario packages
The system SHALL allow grouping multiple strategies into a named scenario for comparison.

#### Scenario: Create a competency scenario
- **WHEN** a user creates a scenario "Max budget" with 3 strategies: external (2 pers, 80000 kr) + training (1 pers, 5000 kr)
- **THEN** `total_cost` is computed as 85000, `total_lead_time_days` as 45

### Requirement: Automatic risk level computation
The system SHALL compute scenario risk level based on strategy types: external → medium, external_temp → low, training-only → medium, mixed internal+training → low.

#### Scenario: Risk computation for mixed strategy
- **WHEN** a scenario contains both "internal" and "training" strategies
- **THEN** `risk_level` is "low"

### Requirement: Earliest completion date
The system SHALL compute `earliest_completion` as today + `total_lead_time_days`.

#### Scenario: Completion date computation
- **WHEN** a scenario has `total_lead_time_days=45` and today is 2026-07-15
- **THEN** `earliest_completion` is 2026-08-29

### Requirement: Select a competency scenario
The system SHALL allow selecting one scenario as the active plan, which becomes the reference for progress tracking.

#### Scenario: Scenario selection
- **WHEN** a user selects scenario "Låg budget" as the active plan
- **THEN** its strategies are promoted to active tracking and other scenarios are marked as alternatives
