# rollout-plan-review Specification

## Purpose

Multi-dimensional plan review that evaluates a rollout plan across 9 dimensions (behavioral science, risk, competency, timeline, stakeholders, ISO compliance, org change, budget, training) with 42 predefined criteria. Generates a readiness score and actionable findings.

## ADDED Requirements

### Requirement: Create a multi-dimensional plan review
The system SHALL allow creating a plan review for a rollout project, optionally scoped to a specific scenario. Reviews SHALL automatically create 9 dimension records with predefined criteria.

#### Scenario: Create a plan review
- **WHEN** a user creates a plan review on a project with no scenario selected
- **THEN** 9 dimensions are created with their respective criteria (42 total), all in draft state

#### Scenario: Create a scenario-specific review
- **WHEN** a user creates a plan review scoped to scenario "Tight deadline"
- **THEN** the review references the scenario and its overrides are considered in the evaluation

### Requirement: Score criteria on a 0-5 scale
Each criterion SHALL be scored 0-5 (Saknas helt → Utmärkt) with an optional finding comment.

#### Scenario: Score criteria
- **WHEN** a reviewer scores "ADKAR — Är alla fem faser representerade?" as 4 with comment "Alla faser finns men Desire-fasen saknar konkreta nudges"
- **THEN** the score and comment are stored and contribute to the dimension average

### Requirement: Compute dimension and overall scores
The system SHALL compute dimension score as the average of its criteria scores. Overall score SHALL be the average of dimension scores.

#### Scenario: Score computation
- **WHEN** the Behavioral dimension has 8 criteria with an average of 3.875 (normalized to 77.5)
- **THEN** the dimension score is 77.5 and rating is "Strong"

### Requirement: Overall rating thresholds
The system SHALL map overall scores to ratings: ≥90 Excellent, ≥75 Strong, ≥60 Adequate, ≥40 Weak, <40 Critical.

#### Scenario: Strong overall rating
- **WHEN** overall score is 82 (average of 9 dimension scores)
- **THEN** overall rating is "Strong" with green indicator

### Requirement: Action items from criteria
Criteria flagged as `action_required` SHALL generate rollout.task items for follow-up.

#### Scenario: Generate action from finding
- **WHEN** a criterion "Kommunikationsplan" is scored 1 with `action_required=True` and finding "Saknas helt för mellanchefer"
- **THEN** a `rollout.task` is created in the relevant phase with the finding as description

### Requirement: Approval workflow
Plan reviews with `approval_required=True` SHALL require approval before findings become actionable.

#### Scenario: Approve a review
- **WHEN** a reviewer submits a review for approval and the project manager approves it
- **THEN** `approved_by_id` is set and action items are created
