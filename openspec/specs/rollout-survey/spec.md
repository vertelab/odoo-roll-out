# rollout-survey Specification

## Purpose

Bridge between the survey module and rollout for Key.se OBMS-style pulse
measurement. Completed survey inputs become `rollout.sentiment` entries:
scale answers (1-5) map to the score, text answers to the comment, and the
survey's project/dimension/wave configuration is copied onto each entry.

## ADDED Requirements

### Requirement: Survey rollout configuration
A survey SHALL be linkable to a rollout project, optional phase, OBMS
dimension (structure/culture/behaviour), pulse wave (baseline/midline/
endline), and marked as generating sentiment entries.

#### Scenario: Configure an OBMS baseline survey
- **WHEN** an administrator links a survey to a rollout project, sets the
  dimension to `culture` and the wave to `baseline`
- **THEN** the survey shows a "Rollout / OBMS" page with these fields and a
  "Generate Sentiment" button

### Requirement: Generate sentiment entries from completed inputs
The system SHALL generate `rollout.sentiment` entries from completed
(non-test) survey inputs, mapping scale answers (1-5) to the average score
and text answers to the comment.

#### Scenario: Scale and text answers
- **WHEN** a done input has a scale answer of 4 and a text answer
  "Känns krångligt med rapporterna"
- **THEN** a sentiment entry is created with score 4, the text as comment,
  the configured dimension/wave, and the respondent as user

### Requirement: Idempotent generation
Generating sentiment entries from the same survey input more than once
SHALL NOT create duplicates.

#### Scenario: Button pressed twice
- **WHEN** "Generate Sentiment" is pressed twice for the same survey
- **THEN** only one sentiment entry exists per completed input
