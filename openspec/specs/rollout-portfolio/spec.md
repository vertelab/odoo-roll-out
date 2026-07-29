# rollout-portfolio Specification

## Purpose

Aggregated view of an employee's Odoo-related competencies, completed training, earned badges, and adoption metrics. Serves as the employee's "Odoo CV" within the rollout context.

## ADDED Requirements

### Requirement: Aggregate employee skills
The system SHALL aggregate all hr.employee.skill records for an employee, including certification dates, expiration dates, and linked ISO standards.

#### Scenario: Retrieve employee skills
- **WHEN** an employee has skills "CRM Fundamentals (Level 2, cert 2026-04-01)" and "ISO 9001 Awareness (cert 2026-03-15)"
- **THEN** the portfolio returns both skills with their level, certification date, and standard

### Requirement: Aggregate completed courses
The system SHALL aggregate completed slide.channel courses for an employee, including completion date and any certification awarded.

#### Scenario: Completed courses in portfolio
- **WHEN** an employee completed "CRM Fundamentals" and "Advanced Pipeline Management" courses
- **THEN** the portfolio returns both courses with completion dates

### Requirement: Aggregate earned badges
The system SHALL aggregate gamification badges earned by the employee.

#### Scenario: Badges in portfolio
- **WHEN** an employee has badges "CRM Champion (Bronze)" and "First 100 Leads"
- **THEN** the portfolio returns both badges with award dates and levels

### Requirement: Adoption metrics
The system SHALL provide adoption metrics: current login streak, total karma, and tasks completed in active rollouts.

#### Scenario: Adoption summary
- **WHEN** an employee has 42-day login streak, 850 karma, and 12 completed rollout tasks
- **THEN** the portfolio returns these metrics in the adoption summary

### Requirement: Rollout progress per employee
The system SHALL show which rollouts the employee is participating in and their progress within each.

#### Scenario: Multi-rollout employee
- **WHEN** an employee is in "Odoo CRM rollout" (progress 78%) and "ISO 9001 rollout" (progress 45%)
- **THEN** the portfolio shows both with progress bars
