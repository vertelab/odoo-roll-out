# Tasks: rollout-core

## 1. Module Setup

- [x] 1.1 Create `rollout/` module skeleton (`__manifest__.py`, `__init__.py`, depends: base, mail)
- [x] 1.2 Create `security/ir.model.access.csv` with access rules for all models
- [x] 1.3 Create `security/rollout_security.xml` with record rules (project-scoped visibility)
- [x] 1.4 Register module in `__manifest__.py` with category, version (18.0.1.0.0), author (Vertel Sverige AB)

## 2. Core Models — Project & Phase

- [x] 2.1 Implement `rollout.project` model with fields: name, customer_id, project_manager_id, team_member_ids, sponsor_id, state, planning_mode, date_start, date_launch
- [x] 2.2 Implement `rollout.phase` model with adkar_phase Selection, duration_days, sequence, gate fields, computed date_start/date_end
- [x] 2.3 Implement forward timeline computation in `rollout.phase._compute_dates()`
- [x] 2.4 Implement backward timeline computation in `rollout.phase._compute_dates()`
- [x] 2.5 Implement `rollout.task` model with phase_id, role_id, assigned_to, deadline, state tracking
- [x] 2.6 Add `models/__init__.py` importing all model files

## 3. Role & Competency Models

- [x] 3.1 Implement `rollout.role` model with skill_ids, course_ids, badge_ids, task_template_ids
- [x] 3.2 Implement `rollout.competency.target` model with skill_id, skill_level_id, target_count, deadline_date, computed current_count/gap/state
- [x] 3.3 Implement `_compute_current_count()` querying `hr.employee.skill`
- [x] 3.4 Implement `_compute_state()` with achieved/missed/at_risk/in_progress/planned logic
- [x] 3.5 Implement `rollout.competency.strategy` model with strategy_type, planned_count, cost_per_person, lead_time_days, achieved_count
- [x] 3.6 Implement `rollout.competency.scenario` model with total_cost, total_lead_time_days, earliest_completion, risk_level computation

## 4. Risk & Scenario Models

- [x] 4.1 Implement `rollout.risk` model with probability, impact, computed risk_score, mitigation, trigger_event, owner_id, state
- [x] 4.2 Implement `rollout.scenario` model with override_date_start, override_date_launch, phase_adjustment_ids, risk_level, adoption_estimate, cost_estimate, selected

## 5. Behavioral Models

- [x] 5.1 Implement `rollout.sentiment` model with user_id, project_id, phase_id, score, free_text, ai_hotspot
- [x] 5.2 Implement `rollout.nudge` model with trigger_event Selection, nudge_type Selection, template Char, role_id, phase_id
- [x] 5.3 Implement nudge template rendering with placeholder substitution (`{user}`, `{role}`, etc.)

## 6. Organizational Change Model

- [x] 6.1 Implement `rollout.org_change` model with change_type Selection, department_id, job_ids, employee_ids, description, status
- [x] 6.2 Add status lifecycle: planned → in_progress → done

## 7. Plan Review Models

- [x] 7.1 Implement `rollout.plan.review` model with reviewer_id, scenario_id, state, computed overall_score/overall_rating, summary, recommendations
- [x] 7.2 Implement `_compute_overall()` averaging dimension scores
- [x] 7.3 Implement `rollout.plan.review.dimension` model with dimension Selection, score, computed rating, SWOT fields
- [x] 7.4 Implement `rollout.plan.review.criterion` model with sequence, name, description, score (0-5), finding, action_required
- [x] 7.5 Create `data/review_criteria_data.xml` with all 42 predefined criteria across 9 dimensions

## 8. Portfolio Model

- [x] 8.1 Implement `rollout.portfolio` as AbstractModel with `get_employee_portfolio(employee_id)` method
- [x] 8.2 Implement skills aggregation from `hr.employee.skill`
- [x] 8.3 Implement courses aggregation from `slide.channel` completions
- [x] 8.4 Implement badges aggregation from `gamification.badge.user`
- [x] 8.5 Implement adoption metrics aggregation (karma, streak, tasks)

## 9. Views — Core

- [x] 9.1 Create `views/rollout_project_views.xml` — tree, form, kanban views for rollout.project
- [x] 9.2 Create `views/rollout_phase_views.xml` — tree, form views with timeline visualization
- [x] 9.3 Create `views/rollout_task_views.xml` — kanban, tree, form views for tasks
- [x] 9.4 Create `views/rollout_role_views.xml` — form view with skill/course/badge tabs
- [x] 9.5 Create `views/rollout_menus.xml` — top-level menu "Rollout" with submenus

## 10. Views — Risk, Scenario, Competency

- [x] 10.1 Create `views/rollout_risk_views.xml` — tree, form views with risk matrix widget
- [x] 10.2 Create `views/rollout_scenario_views.xml` — form, comparison views
- [x] 10.3 Create `views/rollout_sentiment_views.xml` — kanban, form, pivot, graph views
- [x] 10.4 Create `views/rollout_nudge_views.xml` — tree, form views
- [x] 10.5 Create `views/rollout_org_change_views.xml` — tree, form views

## 11. Views — Competency Targets & Strategies

- [x] 11.1 Create `views/rollout_competency_target_views.xml` — tree, form with progress bar
- [x] 11.2 Create `views/rollout_competency_strategy_views.xml` — tree embedded in target form
- [x] 11.3 Create `views/rollout_competency_scenario_views.xml` — comparison view with cost/risk/leadtime

## 12. Views — Plan Review & Portfolio

- [x] 12.1 Create `views/rollout_plan_review_views.xml` — form with dimension tabs, overall score gauge
- [x] 12.2 Create `views/rollout_plan_review_criterion_views.xml` — embedded tree with score widget
- [x] 12.3 Create `views/rollout_portfolio_views.xml` — employee CV view template

## 13. Data Files

- [x] 13.1 Create `data/review_criteria_data.xml` with 42 criteria records
- [ ] 13.2 Optionally create `data/rollout_demo.xml` with sample project, phases, roles, risks

## 14. Bridge Module — rollout_bpm

- [x] 14.1 Create `rollout_bpm/` module (`auto_install=True`, depends: rollout, bpm_workflow)
- [x] 14.2 Implement `bpm.workflow` extension adding rollout_project_id link
- [x] 14.3 Implement view inheritance adding "View as BPMN Process" button on rollout.project

## 15. Bridge Module — rollout_mgmtsystem

- [x] 15.1 Create `rollout_mgmtsystem/` module (`auto_install=True`, depends: rollout, mgmtsystem)
- [x] 15.2 Implement direct link connecting rollout.project/phase to mgmtsystem references
- [x] 15.3 Implement clause and policy links on rollout.phase form

## 16. Bridge Module — rollout_dashboard

- [x] 16.1 Create `rollout_dashboard/` module (`auto_install=True`, depends: rollout, dashboard_vrtl)
- [x] 16.2 Create adoption overview dashboard (defined, charts via dashboard_vrtl YAML)
- [x] 16.3 Create sentiment analysis dashboard (defined)
- [x] 16.4 Create risk radar dashboard (defined)
- [x] 16.5 Create plan readiness dashboard (defined)

## 17. Bridge Module — rollout_gamification

- [x] 17.1 Create `rollout_gamification/` module (`auto_install=True`, depends: rollout, gamification)
- [x] 17.2 Create rollout-specific badges (ADKAR phase completion, skill achievement, streak milestones) — 11 badges
- [x] 17.3 Create rollout-specific challenges (first week login, course completion race)
- [x] 17.4 Create rollout-specific goals structure (linked to competency targets)

## 18. Bridge Module — rollout_lms

- [x] 18.1 Create `rollout_lms/` module (`auto_install=True`, depends: rollout, website_slides)
- [x] 18.2 Implement slide.channel extension adding rollout_role_id link for auto-association
- [x] 18.3 Implement course completion → competency.target progress update trigger structure

## 19. Polish & Documentation

- [x] 19.1 Add i18n support — Swedish sv.po with 270+ translations
- [x] 19.2 Write `README.md` with module overview, installation, and configuration guide
- [x] 19.3 Add `static/description/icon.png`
- [x] 19.4 Run linter and fix all warnings
- [x] 19.5 Verify all specs are satisfied with manual test scenarios
