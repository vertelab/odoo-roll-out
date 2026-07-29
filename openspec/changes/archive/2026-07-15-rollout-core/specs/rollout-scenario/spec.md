# rollout-scenario Specification

## Purpose

What-if scenario analysis for rollout timelines. Compare alternative start dates, compressed phases, and risk levels against the baseline plan.

## ADDED Requirements

### Requirement: Create alternative timeline scenarios
The system SHALL allow creating scenarios that override project start date, go-live date, or individual phase durations.

#### Scenario: Create a compressed scenario
- **WHEN** a user creates a scenario "Tight deadline" with `override_date_launch` 30 days earlier than baseline
- **THEN** the scenario stores the override and can be compared against the baseline

### Requirement: Scenario phase adjustments
Each scenario SHALL support per-phase duration overrides.

#### Scenario: Adjust specific phases in a scenario
- **WHEN** a user sets Awareness to 7 days (from 14) and Knowledge to 20 days (from 30) in a scenario
- **THEN** only those phases differ from baseline; other phases use project defaults

### Requirement: Scenario risk and cost estimation
Each scenario SHALL support risk level, adoption estimate, and cost estimate fields for comparison.

#### Scenario: Compare two scenarios
- **WHEN** Scenario A has risk "low", adoption 90%, cost 50 000 and Scenario B has risk "high", adoption 65%, cost 10 000
- **THEN** the comparison view shows both scenarios side by side with a visual risk indicator

### Requirement: Select a scenario as active plan
The system SHALL allow marking one scenario as selected, which becomes the reference for plan reviews.

#### Scenario: Select a scenario
- **WHEN** a user sets `selected=True` on Scenario A
- **THEN** Scenario A is visually highlighted and used as default for plan reviews
