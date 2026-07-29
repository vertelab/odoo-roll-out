# rollout-nudge Specification

## Purpose

Behavioral nudging engine for rollout projects. Define template-based nudges triggered by events to influence user behavior using social proof, loss aversion, and default-effect principles.

## ADDED Requirements

### Requirement: Define nudge with trigger and template
The system SHALL allow creating nudges with an event trigger type, a message template with placeholders, and a target role or phase.

#### Scenario: Create a social proof nudge
- **WHEN** a user creates a nudge with `trigger_event='course_completed'`, `nudge_type='social_proof'`, template "7 av 10 kollegor har redan klarat {course_name}!", and target role "CRM-användare"
- **THEN** the nudge is stored and evaluated when the trigger event fires

### Requirement: Nudge trigger events
The system SHALL support trigger events: course_completed, login_streak, phase_transition, badge_awarded, competency_milestone, and custom.

#### Scenario: Login streak trigger
- **WHEN** a user reaches a 7-day Odoo login streak
- **THEN** any nudge with `trigger_event='login_streak'` targeting that user's role is evaluated and displayed

### Requirement: Template placeholder rendering
Nudge templates SHALL support placeholders: {user}, {role}, {phase}, {course_name}, {badge_name}, {streak_days}, {team_progress}.

#### Scenario: Template rendering
- **WHEN** template "{user}, du har {streak_days} dagars streak — bara 3 dagar kvar till CRM Champion!" is rendered for user "Anna" with 11 streak days
- **THEN** the rendered message is "Anna, du har 11 dagars streak — bara 3 dagar kvar till CRM Champion!"

### Requirement: Nudge scoped to role or phase
Each nudge SHALL be optionally scoped to a specific role, phase, or both.

#### Scenario: Phase-scoped nudge
- **WHEN** a nudge is scoped to the Knowledge phase and the project is in the Desire phase
- **THEN** the nudge is not triggered until the project enters the Knowledge phase
