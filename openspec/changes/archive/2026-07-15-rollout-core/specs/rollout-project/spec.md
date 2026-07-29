# rollout-project Specification

## Purpose

Manage multiple parallel Odoo rollout projects, each with its own project organization, ADKAR phases, risks, competency targets, and sentiment tracking.

## ADDED Requirements

### Requirement: Create and manage rollout projects
The system SHALL allow creation of multiple independent rollout projects, each with a customer, project manager, team members, and a change sponsor from the customer organization.

#### Scenario: Create a new rollout project
- **WHEN** a user creates a `rollout.project` with name, customer, project manager, and sponsor
- **THEN** the project is created in `draft` state with `planning_mode` defaulting to `backward`

#### Scenario: Multiple parallel projects
- **WHEN** a user creates a second rollout project for a different customer
- **THEN** both projects coexist independently with separate phases, risks, and teams

### Requirement: Project state lifecycle
The system SHALL support states: draft → active → completed / cancelled. Transitions SHALL be audited via mail.thread tracking.

#### Scenario: Activate a project
- **WHEN** a project in `draft` state with at least one phase is activated
- **THEN** the state changes to `active` and all phase dates are recomputed

### Requirement: Timeline planning modes
The system SHALL support two planning modes: forward (from start date) and backward (from go-live date). Phase dates SHALL be computed accordingly.

#### Scenario: Forward planning
- **WHEN** `planning_mode` is `forward` and `date_start` is set to 2026-03-01
- **THEN** phases compute their `date_start`/`date_end` sequentially forward from the project start date

#### Scenario: Backward planning
- **WHEN** `planning_mode` is `backward` and `date_launch` is set to 2026-06-01
- **THEN** phases compute their dates backward from the go-live date, and the required start date is displayed
