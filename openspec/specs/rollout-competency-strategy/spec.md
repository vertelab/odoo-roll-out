# rollout-competency-strategy Specification

## Purpose

Define strategies for achieving competency targets: internal reassignment, external recruitment, training/development, or temporary consultants. Each strategy has cost, lead time, and achievement tracking.

## ADDED Requirements

### Requirement: Define strategies for a competency target
The system SHALL allow creating strategies per competency target with type, planned count, cost, and lead time.

#### Scenario: Create an external recruitment strategy
- **WHEN** a user creates a strategy "Rekrytera tillverkare" with type "external", planned_count 2, cost_per_person 40000, lead_time_days 45
- **THEN** the strategy computes `cost_total=80000` and is linked to the target

### Requirement: Strategy types
The system SHALL support strategy types: internal, external, training, external_temp.

#### Scenario: Mixed strategies for one target
- **WHEN** a target needs 3 people and strategies are: internal (1 person, 0 kr, 7 days), training (2 people, 5000 kr, 14 days)
- **THEN** both strategies are tracked independently and their achievement counts sum toward the target

### Requirement: Strategy achievement tracking
Each strategy SHALL track `achieved_count` separately from `planned_count`.

#### Scenario: Partial achievement
- **WHEN** an external strategy planned for 2 people has hired 1 person
- **THEN** `achieved_count` is 1 and the strategy state remains `active`

### Requirement: Strategy linked to operational models
Strategies SHALL support optional links to hr.job (recruitment), slide.channel (training), and hr.applicant (candidates).

#### Scenario: Training strategy linked to LMS course
- **WHEN** a training strategy is linked to a slide.channel "Manufacturing Advanced"
- **THEN** the link is navigable and course completion updates the strategy's achieved_count
