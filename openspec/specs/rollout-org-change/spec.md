# rollout-org-change Specification

## Purpose

Model organizational changes that occur as part of an Odoo rollout: new departments, restructured teams, new roles, changed reporting lines.

## ADDED Requirements

### Requirement: Define organizational changes
The system SHALL allow defining org changes with type, description, affected departments, jobs, and employees.

#### Scenario: Define a new department
- **WHEN** a user creates an org change of type "new_dept" with name "Digital Transformation Office" linked to the Ability phase
- **THEN** the change is stored and visible in the project's org change register

### Requirement: Org change types
The system SHALL support change types: new_dept, restructure, new_role, merge, split, reporting, and other.

#### Scenario: Reporting line change
- **WHEN** a user creates an org change of type "reporting" describing that the CRM team now reports to the COO instead of the Sales Director
- **THEN** the change is categorized and linked to affected employees

### Requirement: Org change lifecycle
Org changes SHALL progress through states: planned → in_progress → done.

#### Scenario: Complete an org change
- **WHEN** a "new_role" org change transitions from in_progress to done
- **THEN** the change is marked complete and the project progress is updated

### Requirement: Org changes linked to HR models
Org changes SHALL support optional links to hr.department, hr.job, and hr.employee for downstream integration.

#### Scenario: Link org change to HR entities
- **WHEN** an org change of type "new_dept" is linked to an existing hr.department
- **THEN** the link is stored and navigable from the org change view
