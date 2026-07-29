# rollout-phase Specification

## Purpose

Model ADKAR phases within a rollout project, with gates that control progression and timeline computation in both forward and backward planning modes.

## ADDED Requirements

### Requirement: ADKAR phase modeling
The system SHALL support five ADKAR phases: Awareness, Desire, Knowledge, Ability, Reinforcement. Each phase SHALL have a configurable duration and sequence.

#### Scenario: Define a complete ADKAR sequence
- **WHEN** a user adds five phases to a project: Awareness (14d), Desire (21d), Knowledge (30d), Ability (14d), Reinforcement (90d)
- **THEN** the phases are ordered by sequence and their dates are computed automatically

### Requirement: Phase gates
Each phase MAY have a gate that blocks progression to the next phase. Gate types SHALL include: none, approval, metric, completion.

#### Scenario: Metric gate blocks progression
- **WHEN** a phase has `gate_type='metric'` with `gate_metric=80` and the measured value is 65
- **THEN** `gate_passed` remains False and the next phase is visually marked as blocked

#### Scenario: Completion gate passes
- **WHEN** a phase has `gate_type='completion'` and all tasks in that phase are done
- **THEN** `gate_passed` is set to True and the next phase becomes active

### Requirement: Forward timeline computation
Phases SHALL compute dates forward when `project.planning_mode='forward'`.

#### Scenario: Forward computation with three phases
- **WHEN** project starts 2026-03-01 with phases of 14, 21, and 30 days
- **THEN** Phase 1 ends 2026-03-15, Phase 2 runs 2026-03-16 to 2026-04-05, Phase 3 runs 2026-04-06 to 2026-05-05

### Requirement: Backward timeline computation
Phases SHALL compute dates backward when `project.planning_mode='backward'`.

#### Scenario: Backward computation from go-live
- **WHEN** `date_launch` is 2026-06-01 and the last phase has 14 days duration
- **THEN** the last phase starts 2026-05-18, and earlier phases compute backward from there
