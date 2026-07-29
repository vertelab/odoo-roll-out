# Rollout — Organizational Change & Adoption Platform

Beteendevetenskaplig Odoo-rollout med ADKAR, risk, kompetensmål, nudging och plangranskning.

## Overview

`rollout` är en fristående Odoo-modul för att orkestrera verksamhetsförflyttning vid Odoo-implementeringar. Modulen kombinerar beteendevetenskap, ledningssystem, och kompetensstyrning i ett sammanhållet verktyg inuti Odoo.

## Features

- **ADKAR Phases**: Awareness, Desire, Knowledge, Ability, Reinforcement med framåt/bakåt tidtabell och gates
- **Risk Register**: Probabilitet × impact scoring, mitigation plans, trigger events
- **Competency Targets**: "3 personer med nivå X senast datum Y" — automatisk gap-tracking mot anställdas skills
- **Strategies**: Intern omfördelning, extern rekrytering, utbildning, konsulter med kostnad och ledtid
- **Scenarios**: Jämför alternativa tidslinjer, budgetar, och kompetensstrategier
- **Sentiment**: Pulsmätning med AI hotspot-detection
- **Nudging**: Mallbaserade beteendenudges triggade av events
- **Plan Review**: Flerdimensionell granskning (9 dimensioner, 42 kriterier) med readiness scoring
- **Portfolio**: Aggregerad CV-vy över medarbetares skills, kurser, badges och adoption
- **Organizational Changes**: Modellera omorganisationer som del av rollout

## Installation

```bash
# Kopiera till Odoo addons path
cp -r rollout /path/to/odoo/addons/

# Uppdatera modullistan och installera
# Settings → Apps → Update Apps List → sök "Rollout" → Install
```

## Dependencies

**Required**: `base`, `mail` (Odoo core)

**Optional** (bridge modules, auto-installed when present):
- `bpm_workflow` → `rollout_bpm`: BPMN process engine integration
- `mgmtsystem` → `rollout_mgmtsystem`: ISO management system integration
- `dashboard_vrtl` → `rollout_dashboard`: BI dashboards
- `gamification` → `rollout_gamification`: Badges, challenges, leaderboards
- `website_slides` → `rollout_lms`: eLearning integration

## Usage

### Quick Start

1. Create a `rollout.project` (Rollout → Projects → Create)
2. Add ADKAR phases with durations and gates
3. Define roles with required skills, courses, and badges
4. Add risks with probability/impact scoring
5. Create competency targets with strategies
6. Run a plan review to evaluate readiness

### Timeline Planning

Two modes are supported:
- **Forward**: Set start date → go-live date is computed
- **Backward**: Set go-live date → required start date is computed

### Plan Review

Create a `rollout.plan.review` to evaluate your plan across 9 dimensions:
- Behavioral Science, Risk, Competency, Timeline, Stakeholders
- ISO/Compliance, Org Change, Budget, Training

Each dimension has predefined criteria scored 0-5. The review generates a readiness score (0-100).

## Models

| Model | Description |
|-------|-------------|
| `rollout.project` | Rollout project with phases, risks, targets |
| `rollout.phase` | ADKAR phase with timeline and gate |
| `rollout.task` | Checklist item within a phase |
| `rollout.role` | Role with skill/course/badge requirements |
| `rollout.risk` | Risk with probability × impact scoring |
| `rollout.scenario` | Alternative timeline scenario |
| `rollout.sentiment` | Pulse survey entry |
| `rollout.nudge` | Behavioral nudge with trigger + template |
| `rollout.org_change` | Organizational change record |
| `rollout.competency.target` | Competency target with auto gap-tracking |
| `rollout.competency.strategy` | Strategy: internal/external/training |
| `rollout.competency.scenario` | Competency scenario package |
| `rollout.plan.review` | Multi-dimensional plan review |
| `rollout.plan.review.dimension` | Review dimension with SWOT |
| `rollout.plan.review.criterion` | Review criterion (0-5 scoring) |
| `rollout.portfolio` | Abstract model: employee CV aggregation |

## License

AGPL-3 — Copyright (C) 2026 Vertel Sverige AB
