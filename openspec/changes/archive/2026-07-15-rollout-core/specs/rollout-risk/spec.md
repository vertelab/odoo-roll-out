# rollout-risk Specification

## Purpose

Risk register for rollout projects with probability × impact scoring, mitigation plans, trigger events, and lifecycle tracking.

## ADDED Requirements

### Requirement: Risk register with scoring
The system SHALL allow creating risks with probability (1-5) and impact (1-5) ratings. The risk score SHALL be computed as probability × impact.

#### Scenario: Create a risk with scoring
- **WHEN** a user creates a risk "Key person leaves" with probability 3 and impact 5
- **THEN** `risk_score` is computed as 15 and the risk appears in the project risk register

### Requirement: Risk lifecycle tracking
Risks SHALL progress through states: identified → monitoring → materialized → mitigated.

#### Scenario: Risk materializes
- **WHEN** a risk in "monitoring" state has its trigger event occur
- **THEN** the user can transition it to "materialized" state and link mitigation actions

### Requirement: Risk with mitigation and trigger
Each risk SHALL support a mitigation plan, trigger event description, and an owner.

#### Scenario: Complete risk definition
- **WHEN** a user creates a risk with mitigation "Cross-train backup person", trigger "Employee gives notice", and owner "Project Manager"
- **THEN** all fields are stored and visible in the risk detail view

### Requirement: Risk linked to phase
Risks MAY be linked to a specific rollout phase for contextual tracking.

#### Scenario: Phase-specific risk
- **WHEN** a risk "Training material not ready" is linked to the Knowledge phase
- **THEN** the risk is filtered and highlighted when viewing that phase
