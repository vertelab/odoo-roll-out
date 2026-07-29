# rollout-role Specification

## Purpose

Define role-specific requirements for a rollout: which competencies, courses, badges, and onboarding checklists a person in that role needs to complete.

## ADDED Requirements

### Requirement: Role definition with competency requirements
The system SHALL allow defining rollout roles with required skills at specified levels.

#### Scenario: Define a CRM user role
- **WHEN** a user creates a role "CRM-användare" with required skills: "CRM Fundamentals (Level 2)", "Sales Pipeline (Level 1)"
- **THEN** the role stores the skill-level associations and can be linked to rollout phases

### Requirement: Role linked to LMS courses
The system SHALL support linking roles to required LMS courses via `slide.channel`.

#### Scenario: Link courses to a role
- **WHEN** a user adds a course "Odoo CRM Basics" to the CRM-användare role
- **THEN** the course association is stored and can trigger nudge notifications when employees haven't completed it

### Requirement: Role linked to gamification badges
The system SHALL support linking roles to required gamification badges.

#### Scenario: Link badges to a role
- **WHEN** a user adds badges "CRM Champion (Bronze)" and "First 100 Leads" to the CRM-användare role
- **THEN** the badge associations are stored and progress can be tracked per employee

### Requirement: Role with onboarding task templates
The system SHALL allow linking role-specific task templates that auto-generate checklist items when a person is assigned to that role.

#### Scenario: Auto-generate checklist from role template
- **WHEN** an employee is assigned to the CRM-användare role with 5 task templates
- **THEN** 5 `rollout.task` items are created for that employee in the current phase
