# rollout-sentiment Specification

## Purpose

Pulse survey tracking for rollout projects. Collect sentiment scores and free-text feedback from users, with AI-powered hotspot detection and trend analysis.

## ADDED Requirements

### Requirement: Record sentiment entries
The system SHALL allow recording sentiment entries per user per project, with a numeric score and optional free-text comment.

#### Scenario: User submits sentiment
- **WHEN** a user submits a sentiment entry with score 4 (out of 5) and comment "Börjar förstå CRM-flödet nu"
- **THEN** the entry is stored with timestamp, user, and project reference

### Requirement: Sentiment trend analysis
The system SHALL compute average sentiment per day, week, and month for trend visualization.

#### Scenario: Weekly trend
- **WHEN** 10 users submit sentiment scores averaging 3.2 in week 1 and 4.1 in week 2
- **THEN** the trend shows an upward arrow with +0.9 improvement

### Requirement: AI hotspot detection
When AI service is configured, the system SHALL analyze free-text comments to detect hotspots (departments or topics with declining sentiment).

#### Scenario: AI detects a hotspot
- **WHEN** AI analyzes comments and finds 5 of 8 comments from the Finance department mention "svårt" or "förvirrande"
- **THEN** the Finance department is flagged as a hotspot with a notification to the project manager

### Requirement: Sentiment linked to phase
Sentiment entries SHALL be linkable to a rollout phase for phase-specific pulse tracking.

#### Scenario: Phase-specific pulse
- **WHEN** sentiment is collected during the Knowledge phase
- **THEN** the entries are tagged with the phase and can be filtered per phase in reports
