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

### Requirement: OBMS dimension tagging (Key.se)
Sentiment entries SHALL be taggable with an OBMS dimension — structure, culture or behaviour — so pulses can be measured per organizational layer.

#### Scenario: OBMS dimension snapshot
- **WHEN** baseline pulses are recorded as structure=2, culture=3, behaviour=2 for a project
- **THEN** `get_obms_snapshot(project, 'baseline')` returns `{'structure': 2.0, 'culture': 3.0, 'behavior': 2.0}`

### Requirement: Pulse wave tracking (nuläge → önskat läge)
Sentiment entries SHALL carry a pulse wave — baseline, midline or endline — to compare the starting point with the target state over the rollout.

#### Scenario: Baseline vs midline comparison
- **WHEN** the same OBMS dimension is measured at baseline (2.0) and midline (4.0)
- **THEN** the wave filter returns the per-dimension averages for each wave separately
