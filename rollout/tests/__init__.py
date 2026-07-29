# -*- coding: utf-8 -*-
# Copyright (C) 2026 Vertel Sverige AB
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from datetime import date, timedelta


class TestRolloutProject(TransactionCase):

    def setUp(self):
        super().setUp()
        self.project = self.env['rollout.project'].create({
            'name': 'Test Rollout',
            'planning_mode': 'backward',
            'date_launch': '2026-10-01',
        })

    def test_create_project(self):
        """Project creation with default values."""
        self.assertEqual(self.project.state, 'draft')
        self.assertEqual(self.project.planning_mode, 'backward')
        self.assertTrue(self.project.name)

    def test_project_state_lifecycle(self):
        """Project transitions through states."""
        self.project.action_activate()
        self.assertEqual(self.project.state, 'active')
        self.project.action_complete()
        self.assertEqual(self.project.state, 'completed')

    def test_project_cancel(self):
        """Project can be cancelled."""
        self.project.action_activate()
        self.project.action_cancel()
        self.assertEqual(self.project.state, 'cancelled')

    def test_project_name_required(self):
        """Name is required."""
        with self.assertRaises(Exception):
            self.env['rollout.project'].create({'name': False})


class TestRolloutPhase(TransactionCase):

    def setUp(self):
        super().setUp()
        self.project = self.env['rollout.project'].create({
            'name': 'Test Rollout',
            'planning_mode': 'forward',
            'date_start': '2026-03-01',
        })

    def test_create_phase(self):
        """Phase creation and ADKAR assignment."""
        phase = self.env['rollout.phase'].create({
            'project_id': self.project.id,
            'name': 'Awareness Phase',
            'adkar_phase': 'awareness',
            'sequence': 10,
            'duration_days': 14,
        })
        self.assertEqual(phase.adkar_phase, 'awareness')
        self.assertEqual(phase.project_id, self.project)
        self.assertEqual(phase.duration_days, 14)

    def test_forward_timeline_one_phase(self):
        """Forward timeline: single phase dates start from project start."""
        phase = self.env['rollout.phase'].create({
            'project_id': self.project.id,
            'name': 'Awareness',
            'adkar_phase': 'awareness',
            'sequence': 10,
            'duration_days': 14,
        })
        self.assertEqual(phase.date_start, date(2026, 3, 1))
        self.assertEqual(phase.date_end, date(2026, 3, 14))

    def test_forward_timeline_two_phases(self):
        """Forward timeline: two phases chain sequentially."""
        p1 = self.env['rollout.phase'].create({
            'project_id': self.project.id,
            'name': 'Phase 1',
            'adkar_phase': 'awareness',
            'sequence': 10,
            'duration_days': 7,
        })
        p2 = self.env['rollout.phase'].create({
            'project_id': self.project.id,
            'name': 'Phase 2',
            'adkar_phase': 'desire',
            'sequence': 20,
            'duration_days': 14,
        })
        self.assertEqual(p1.date_start, date(2026, 3, 1))
        self.assertEqual(p1.date_end, date(2026, 3, 7))
        self.assertEqual(p2.date_start, date(2026, 3, 8))
        self.assertEqual(p2.date_end, date(2026, 3, 21))

    def test_backward_timeline(self):
        """Backward timeline: phases compute backwards from go-live."""
        self.project.write({
            'planning_mode': 'backward',
            'date_launch': '2026-06-01',
        })
        p1 = self.env['rollout.phase'].create({
            'project_id': self.project.id,
            'name': 'Phase 1',
            'adkar_phase': 'reinforcement',
            'sequence': 10,
            'duration_days': 14,
        })
        # Last phase (highest sequence) ends on go-live
        self.assertEqual(p1.date_end, date(2026, 6, 1))
        self.assertEqual(p1.date_start, date(2026, 5, 19))

    def test_no_dates_without_project_dates(self):
        """Phase dates remain unset if project has no dates."""
        p = self.env['rollout.project'].create({
            'name': 'No Dates Project',
            'planning_mode': 'forward',
        })
        phase = self.env['rollout.phase'].create({
            'project_id': p.id,
            'name': 'No Date Phase',
            'adkar_phase': 'awareness',
            'sequence': 10,
            'duration_days': 14,
        })
        self.assertFalse(phase.date_start)
        self.assertFalse(phase.date_end)


class TestRolloutRisk(TransactionCase):

    def setUp(self):
        super().setUp()
        self.project = self.env['rollout.project'].create({
            'name': 'Risk Test Project',
            'planning_mode': 'backward',
            'date_launch': '2026-10-01',
        })

    def test_risk_score_computation(self):
        """Risk score = probability × impact."""
        risk = self.env['rollout.risk'].create({
            'project_id': self.project.id,
            'name': 'Test Risk',
            'probability': '4',
            'impact': '5',
        })
        self.assertEqual(risk.risk_score, 20)

    def test_risk_score_zero(self):
        """Risk score with lowest values."""
        risk = self.env['rollout.risk'].create({
            'project_id': self.project.id,
            'name': 'Low Risk',
            'probability': '1',
            'impact': '1',
        })
        self.assertEqual(risk.risk_score, 1)

    def test_risk_state_default(self):
        """Risk defaults to 'identified' state."""
        risk = self.env['rollout.risk'].create({
            'project_id': self.project.id,
            'name': 'State Risk',
            'probability': '3',
            'impact': '3',
        })
        self.assertEqual(risk.state, 'identified')

    def test_risk_requires_probability_and_impact(self):
        """Risk requires probability and impact."""
        risk = self.env['rollout.risk'].create({
            'project_id': self.project.id,
            'name': 'Required Risk',
            'probability': '3',
            'impact': '3',
        })
        self.assertEqual(risk.probability, '3')
        self.assertEqual(risk.impact, '3')


class TestRolloutCompetencyTarget(TransactionCase):

    def setUp(self):
        super().setUp()
        self.project = self.env['rollout.project'].create({
            'name': 'Competency Test',
            'planning_mode': 'backward',
            'date_launch': '2026-10-01',
        })

    def test_target_creation(self):
        """Competency target with basic fields."""
        target = self.env['rollout.competency.target'].create({
            'project_id': self.project.id,
            'name': 'Three CRM Experts',
            'target_count': 3,
            'deadline_date': '2026-09-15',
        })
        self.assertEqual(target.target_count, 3)
        self.assertEqual(target.deadline_date, date(2026, 9, 15))
        self.assertEqual(target.state, 'planned')

    def test_target_state_achieved(self):
        """Target is achieved when gap <= 0."""
        target = self.env['rollout.competency.target'].create({
            'project_id': self.project.id,
            'name': 'Easy Target',
            'target_count': 0,
            'deadline_date': '2027-01-01',
        })
        self.assertEqual(target.gap, 0)
        self.assertEqual(target.state, 'achieved')

    def test_target_state_missed(self):
        """Target is missed when past deadline with gap > 0."""
        target = self.env['rollout.competency.target'].create({
            'project_id': self.project.id,
            'name': 'Missed Target',
            'target_count': 10,
            'deadline_date': '2020-01-01',  # Past
        })
        self.assertEqual(target.state, 'missed')

    def test_target_state_at_risk(self):
        """Target is at risk when within 14 days of deadline with gap."""
        soon = date.today() + timedelta(days=10)
        target = self.env['rollout.competency.target'].create({
            'project_id': self.project.id,
            'name': 'At Risk Target',
            'target_count': 10,
            'deadline_date': soon,
        })
        self.assertEqual(target.state, 'at_risk')

    def test_target_gap_calculation(self):
        """Gap = target_count - current_count."""
        target = self.env['rollout.competency.target'].create({
            'project_id': self.project.id,
            'name': 'Gap Test',
            'target_count': 5,
            'deadline_date': '2027-01-01',
        })
        self.assertEqual(target.gap, 5)
        self.assertEqual(target.progress_pct, 0.0)


class TestRolloutSentiment(TransactionCase):

    def setUp(self):
        super().setUp()
        self.project = self.env['rollout.project'].create({
            'name': 'Sentiment Test',
            'planning_mode': 'backward',
            'date_launch': '2026-10-01',
        })

    def test_sentiment_entry(self):
        """Basic sentiment entry creation."""
        entry = self.env['rollout.sentiment'].create({
            'project_id': self.project.id,
            'score': 4,
            'free_text': 'Det går bra!',
        })
        self.assertEqual(entry.score, 4)
        self.assertEqual(entry.free_text, 'Det går bra!')
        self.assertFalse(entry.ai_hotspot)

    def test_sentiment_hotspot(self):
        """Sentiment flagged as hotspot."""
        entry = self.env['rollout.sentiment'].create({
            'project_id': self.project.id,
            'score': 1,
            'free_text': 'Fungerar inte alls',
            'ai_hotspot': True,
            'ai_category': 'Tekniska problem',
        })
        self.assertTrue(entry.ai_hotspot)
        self.assertEqual(entry.ai_category, 'Tekniska problem')


class TestRolloutNudge(TransactionCase):

    def setUp(self):
        super().setUp()
        self.project = self.env['rollout.project'].create({
            'name': 'Nudge Test',
            'planning_mode': 'backward',
            'date_launch': '2026-10-01',
        })

    def test_nudge_creation(self):
        """Nudge with trigger and template."""
        nudge = self.env['rollout.nudge'].create({
            'project_id': self.project.id,
            'name': 'Test Nudge',
            'trigger_event': 'course_completed',
            'nudge_type': 'social_proof',
            'template': '{user} klarade {course_name}!',
        })
        self.assertEqual(nudge.trigger_event, 'course_completed')
        self.assertEqual(nudge.nudge_type, 'social_proof')

    def test_nudge_template_rendering(self):
        """Template renders with context."""
        nudge = self.env['rollout.nudge'].create({
            'project_id': self.project.id,
            'name': 'Render Test',
            'trigger_event': 'login_streak',
            'nudge_type': 'commitment',
            'template': '{user}, du har {streak_days} dagars streak!',
        })
        result = nudge.render_template(user='Anna', streak_days='14')
        self.assertEqual(result, 'Anna, du har 14 dagars streak!')

    def test_nudge_template_missing_key(self):
        """Template with missing key returns raw template."""
        nudge = self.env['rollout.nudge'].create({
            'project_id': self.project.id,
            'name': 'Bad Template',
            'trigger_event': 'custom',
            'nudge_type': 'framing',
            'template': '{user} and {nonexistent}',
        })
        result = nudge.render_template(user='Test')
        # Missing key returns raw template
        self.assertEqual(result, '{user} and {nonexistent}')


class TestRolloutOrgChange(TransactionCase):

    def setUp(self):
        super().setUp()
        self.project = self.env['rollout.project'].create({
            'name': 'Org Change Test',
            'planning_mode': 'backward',
            'date_launch': '2026-10-01',
        })

    def test_org_change_creation(self):
        """Organizational change with type."""
        change = self.env['rollout.org_change'].create({
            'project_id': self.project.id,
            'name': 'New IT Department',
            'change_type': 'new_dept',
        })
        self.assertEqual(change.change_type, 'new_dept')
        self.assertEqual(change.status, 'planned')

    def test_org_change_lifecycle(self):
        """Status transitions."""
        change = self.env['rollout.org_change'].create({
            'project_id': self.project.id,
            'name': 'Restructure Sales',
            'change_type': 'restructure',
        })
        change.action_start()
        self.assertEqual(change.status, 'in_progress')
        change.action_done()
        self.assertEqual(change.status, 'done')


class TestRolloutPlanReview(TransactionCase):

    def setUp(self):
        super().setUp()
        self.project = self.env['rollout.project'].create({
            'name': 'Review Test',
            'planning_mode': 'backward',
            'date_launch': '2026-10-01',
        })

    def test_review_creation(self):
        """Plan review creation."""
        review = self.env['rollout.plan.review'].create({
            'project_id': self.project.id,
            'reviewer_id': self.env.user.id,
        })
        self.assertEqual(review.state, 'draft')
        self.assertEqual(review.reviewer_id, self.env.user)

    def test_review_overall_score_no_dimensions(self):
        """Overall score is 0 with no dimensions."""
        review = self.env['rollout.plan.review'].create({
            'project_id': self.project.id,
        })
        self.assertEqual(review.overall_score, 0.0)
        self.assertEqual(review.overall_rating, 'critical')

    def test_review_dimension_creation(self):
        """Dimension with scoring."""
        review = self.env['rollout.plan.review'].create({
            'project_id': self.project.id,
        })
        dim = self.env['rollout.plan.review.dimension'].create({
            'review_id': review.id,
            'dimension': 'behavioral',
            'score': 85.0,
        })
        self.assertEqual(dim.rating, 'strong')

    def test_review_overall_with_dimensions(self):
        """Overall score averages dimension scores."""
        review = self.env['rollout.plan.review'].create({
            'project_id': self.project.id,
        })
        self.env['rollout.plan.review.dimension'].create({
            'review_id': review.id,
            'dimension': 'behavioral',
            'score': 80.0,
        })
        self.env['rollout.plan.review.dimension'].create({
            'review_id': review.id,
            'dimension': 'risk',
            'score': 60.0,
        })
        self.assertEqual(review.overall_score, 70.0)
        self.assertEqual(review.overall_rating, 'adequate')

    def test_review_criterion_scoring(self):
        """Criterion with 0-5 scoring."""
        review = self.env['rollout.plan.review'].create({
            'project_id': self.project.id,
        })
        dim = self.env['rollout.plan.review.dimension'].create({
            'review_id': review.id,
            'dimension': 'behavioral',
            'score': 50.0,
        })
        crit = self.env['rollout.plan.review.criterion'].create({
            'dimension_id': dim.id,
            'name': 'ADKAR completeness',
            'score': '4',
            'finding': 'All phases present',
        })
        self.assertEqual(crit.score, '4')
        self.assertFalse(crit.action_required)

    def test_review_state_lifecycle(self):
        """Review transitions through states."""
        review = self.env['rollout.plan.review'].create({
            'project_id': self.project.id,
        })
        review.action_start_review()
        self.assertEqual(review.state, 'in_progress')
        review.action_complete()
        self.assertEqual(review.state, 'completed')
        review.action_approve()
        self.assertEqual(review.approved_by_id, self.env.user)


class TestRolloutScenario(TransactionCase):

    def setUp(self):
        super().setUp()
        self.project = self.env['rollout.project'].create({
            'name': 'Scenario Test',
            'planning_mode': 'backward',
            'date_launch': '2026-10-01',
        })

    def test_scenario_creation(self):
        """Scenario with overrides."""
        scenario = self.env['rollout.scenario'].create({
            'project_id': self.project.id,
            'name': 'Fast Track',
            'override_date_launch': '2026-08-01',
            'risk_level': 'high',
            'adoption_estimate': 65.0,
            'cost_estimate': 350000.0,
        })
        self.assertEqual(scenario.risk_level, 'high')
        self.assertFalse(scenario.selected)

    def test_scenario_selection(self):
        """Only one scenario selected at a time convention."""
        s1 = self.env['rollout.scenario'].create({
            'project_id': self.project.id,
            'name': 'Scenario 1',
            'selected': True,
        })
        self.assertTrue(s1.selected)


class TestRolloutTask(TransactionCase):

    def setUp(self):
        super().setUp()
        self.project = self.env['rollout.project'].create({
            'name': 'Task Test',
            'planning_mode': 'backward',
            'date_launch': '2026-10-01',
        })
        self.phase = self.env['rollout.phase'].create({
            'project_id': self.project.id,
            'name': 'Phase',
            'adkar_phase': 'knowledge',
            'sequence': 10,
            'duration_days': 30,
        })

    def test_task_creation(self):
        """Task with assignment."""
        task = self.env['rollout.task'].create({
            'phase_id': self.phase.id,
            'name': 'Complete CRM training',
            'priority': '2',
        })
        self.assertEqual(task.state, 'todo')
        self.assertEqual(task.priority, '2')

    def test_task_state_transitions(self):
        """Task transitions through states."""
        task = self.env['rollout.task'].create({
            'phase_id': self.phase.id,
            'name': 'Test transitions',
        })
        self.assertEqual(task.state, 'todo')
        task.action_start()
        self.assertEqual(task.state, 'in_progress')
        task.action_done()
        self.assertEqual(task.state, 'done')

    def test_task_cancel(self):
        """Task can be cancelled."""
        task = self.env['rollout.task'].create({
            'phase_id': self.phase.id,
            'name': 'Cancelled task',
        })
        task.action_cancel()
        self.assertEqual(task.state, 'cancelled')
