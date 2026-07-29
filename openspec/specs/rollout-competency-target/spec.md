# rollout-competency-target Specification

## Purpose

Define competency targets for a rollout: "We need X people with skill Y at level Z by date D." Track progress automatically against hr.employee.skill records.

## ADDED Requirements

### Requirement: Define competency targets
The system SHALL allow creating competency targets with a skill, level, target count, and deadline date. Progress SHALL be computed automatically from existing employee skills.

#### Scenario: Create a competency target
- **WHEN** a user creates target "Manufacturing Level 3" with skill "Tillverkningskompetens", level "Nivå 3", target_count 3, deadline 2026-09-15
- **THEN** the target is created and `current_count` is computed from hr.employee.skill records

### Requirement: Automatic gap calculation
The system SHALL compute `gap = target_count − current_count` and `progress_pct = current_count / target_count × 100`.

#### Scenario: Gap shows shortfall
- **WHEN** target_count is 3 and current_count is 1
- **THEN** gap is 2 and progress_pct is 33.3%

### Requirement: Automatic state computation
The system SHALL compute state based on gap and deadline: achieved (gap ≤ 0), missed (past deadline with gap > 0), at_risk (≤ 14 days to deadline with gap > 0), in_progress (current_count > 0), planned (otherwise).

#### Scenario: Target at risk
- **WHEN** gap is 2, deadline is in 10 days
- **THEN** state is `at_risk` and a warning is displayed

#### Scenario: Target achieved
- **WHEN** gap is 0
- **THEN** state is `achieved` and the target is shown with a checkmark

### Requirement: Target linked to phase and role
Each target SHALL be linkable to a rollout phase and a rollout role.

#### Scenario: Phase-linked target
- **WHEN** a competency target is linked to the Knowledge phase and the CRM-användare role
- **THEN** the target appears in the phase detail view and role requirements summary
