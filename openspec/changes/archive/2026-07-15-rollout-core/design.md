# Design: rollout-core

## Context

`rollout-core` introduces a new Odoo module (`rollout`) that orchestrates behavioral science-driven organizational change when deploying Odoo. The module must be fully standalone (dependencies: `base`, `mail` only) with all optional integrations via bridge modules (`auto_install=True`).

**Existing building blocks** already available in Vertel's/Odoo's ecosystem:
- Odoo core: `gamification` (badges, challenges, karma), `website_slides` (LMS), `hr_skills` (competence), `survey` (assessments)
- Vertel: `bpm_workflow` (BPMN engine), `mgmtsystem` + clauses/policy/gap, `hr_skill_esco` (ESCO taxonomy), `hr_onboarding_ce`, `dashboard_vrtl`
- OCA: `mgmtsystem` (audit, review, action, nonconformity), `hr_course`, `project_risk`

**Key constraint**: `rollout` must function without any of these. Bridge modules activate only when dependencies are installed.

## Goals / Non-Goals

**Goals:**
- Provide a standalone Odoo module for managing organizational change during Odoo implementation
- Model ADKAR phases with forward/backward timeline planning
- Track competency targets with gap analysis and multi-strategy scenarios
- Enable behavioral nudging and sentiment analysis
- Support multi-dimensional plan review with scoring criteria
- Remain dependency-free beyond `base` + `mail`

**Non-Goals:**
- In-app walkthroughs / UI overlays (DAP territory)
- Real-time BPMN process execution (delegated to `bpm_workflow` via bridge)
- ISO audit management (delegated to `mgmtsystem` via bridge)
- SCORM/xAPI support (delegated to `website_slides`)
- Mobile-first UX (delegated to Odoo mobile app)

## Decisions

### Decision 1: Module structure — core + bridges

`rollout/` is the core module. Five bridge modules (`rollout_bpm`, `rollout_mgmtsystem`, `rollout_dashboard`, `rollout_gamification`, `rollout_lms`) each `auto_install=True` when their respective dependency is present.

**Rationale**: Keeps the core installable anywhere. Customers without BPM or mgmtsystem get the full behavioral science toolset. Those with the full stack get seamless integration.

**Alternatives considered**: Single monolithic module with `has_module()` checks in Python. Rejected — harder to test, violates separation of concerns, and forces all customers to install unused dependencies conceptually.

### Decision 2: ADKAR as explicit Selection field, not BPM process

`rollout.phase` uses `adkar_phase` as a Selection field (awareness/desire/knowledge/ability/reinforcement). The optional `rollout_bpm` bridge maps phases to `bpm.task` nodes within a `bpm.workflow`.

**Rationale**: ADKAR is a semantic framework, not a technical process. Keeping it as a Selection makes the model self-documenting and allows rich business logic (gate checks, calendar computations) without requiring BPM to be installed.

**Alternatives considered**: Require BPM for all phase management. Rejected — violates the standalone requirement and couples behavioral science to a process engine unnecessarily.

### Decision 3: Timeline — computed fields, not stored

Phase dates (`date_start`, `date_end`) are computed based on `planning_mode`, project dates, and phase durations. This ensures consistency when phases are reordered or durations change.

**Rationale**: Stored dates would go stale on any change. Computed fields with `store=True` give us queryability without inconsistency.

**Alternatives considered**: Store dates and recalculate on write. Rejected — brittle and requires triggers on multiple fields.

### Decision 4: Competency targets as separate model, not hr.skill extension

`rollout.competency.target` is a standalone model that references `hr.skill` and `hr.skill.level`. It does not modify the hr models.

**Rationale**: Competency targets have different lifecycle and semantics than employee skills. A target is a project-level goal ("we need 3 people with skill X"), not a person-level attribute.

### Decision 5: Plan review uses predefined criteria data, not hardcoded logic

The 42 review criteria across 9 dimensions are defined as data (XML records) with a `dimension` field grouping them. This allows consultants to add, modify, or translate criteria without code changes.

**Rationale**: Review criteria are domain knowledge, not algorithm. Different industries may need different criteria. Data-driven design enables customization.

### Decision 6: Nudge model — template + trigger, not code

`rollout.nudge` uses string templates (with `{user}`, `{role}`, `{phase}` placeholders) and event-based triggers (`course_completed`, `login_streak`, `phase_transition`). No Python code per nudge.

**Rationale**: Behavioral consultants should be able to create nudges without development. Template-based approach enables this while keeping the evaluation simple.

## Risks / Trade-offs

| Risk | Impact | Mitigation |
|------|--------|------------|
| **14 new models** is a large surface area for a v1 | High | Phase implementation: core models first, competency/scenario/review in later iterations within the same change |
| **Computed timeline fields** may have performance issues on large phase sets | Low | Phases per project typically < 20. `store=True` + index handles this. |
| **Nudge template rendering** could be brittle with malformed placeholders | Low | Validate templates on save. Use `str.format()` with strict error handling. |
| **Bridge modules** create combinatorial testing burden | Medium | Each bridge is tested independently. Core module tested without any bridges installed. |
| **Sentiment AI analysis** depends on external AI service quality | Medium | Make AI analysis optional/configurable. Fallback to keyword-based analysis. |
| **No migration path** — this is a new module | None | N/A |

## Open Questions

1. **AI provider for sentiment analysis**: Should we use Odoo's built-in AI (`ai_agent`) or allow pluggable providers? Default to `ai_agent` if installed, with a generic interface.
2. **Gamification badge creation**: Should the bridge module auto-create rollout-specific badges, or just link to existing ones? Auto-create with a "Rollout" category.
3. **Multi-company support**: Should `rollout.project` be company-scoped? Yes — add `company_id` field with default multi-company rules.
4. **Notification channels**: How should nudge messages be delivered? Odoo notifications (default) + optional email via `mail.template`.
