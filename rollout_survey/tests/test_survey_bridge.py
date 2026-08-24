"""Tests for the rollout_survey bridge: survey answers -> rollout.sentiment."""

from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestSurveyBridge(TransactionCase):

    def setUp(self):
        super().setUp()
        self.customer = self.env['res.partner'].create({
            'name': 'Survey Test Customer',
            'is_company': True,
        })
        self.partner = self.env['res.partner'].create({
            'name': 'Survey Test Respondent',
        })
        self.user = self.env['res.users'].create({
            'name': 'Survey Test User',
            'login': 'survey_test_user',
            'partner_id': self.partner.id,
        })
        self.project = self.env['rollout.project'].create({
            'name': 'Test Rollout Project',
            'customer_id': self.customer.id,
            'planning_mode': 'forward',
            'date_start': '2026-01-01',
        })
        self.phase = self.env['rollout.phase'].create({
            'project_id': self.project.id,
            'name': 'Awareness',
            'adkar_phase': 'awareness',
            'sequence': 10,
            'duration_days': 14,
        })
        self.survey = self.env['survey.survey'].create({
            'title': 'OBMS Baseline Pulse',
            'rollout_project_id': self.project.id,
            'rollout_phase_id': self.phase.id,
            'rollout_dimension': 'culture',
            'rollout_wave': 'baseline',
        })
        self.question_scale = self.env['survey.question'].create({
            'survey_id': self.survey.id,
            'title': 'How do you feel about the change?',
            'question_type': 'scale',
            'scale_min': 1,
            'scale_max': 5,
        })
        self.question_text = self.env['survey.question'].create({
            'survey_id': self.survey.id,
            'title': 'Anything else?',
            'question_type': 'text_box',
        })
        self.user_input = self.env['survey.user_input'].create({
            'survey_id': self.survey.id,
            'partner_id': self.partner.id,
            'state': 'done',
        })
        self.env['survey.user_input.line'].create({
            'user_input_id': self.user_input.id,
            'question_id': self.question_scale.id,
            'answer_type': 'scale',
            'value_scale': 4,
        })
        self.env['survey.user_input.line'].create({
            'user_input_id': self.user_input.id,
            'question_id': self.question_text.id,
            'answer_type': 'text_box',
            'value_text_box': 'Känns krångligt med rapporterna.',
        })

    def test_prepare_sentiment_values(self):
        """Answers are mapped to a rollout.sentiment value dict."""
        vals = self.user_input._prepare_rollout_sentiment_values()
        self.assertEqual(vals['project_id'], self.project.id)
        self.assertEqual(vals['phase_id'], self.phase.id)
        self.assertEqual(vals['user_id'], self.user.id)
        self.assertEqual(vals['score'], 4)
        self.assertIn('krångligt', vals['comment'])
        self.assertEqual(vals['dimension'], 'culture')
        self.assertEqual(vals['wave'], 'baseline')
        self.assertEqual(vals['survey_input_id'], self.user_input.id)

    def test_generate_sentiment_creates_entry(self):
        """action_generate_sentiment creates one rollout.sentiment entry."""
        self.assertTrue(self.survey.action_generate_sentiment())
        sentiments = self.env['rollout.sentiment'].search([
            ('survey_input_id', '=', self.user_input.id),
        ])
        self.assertEqual(len(sentiments), 1)
        self.assertEqual(sentiments.score, 4)
        self.assertEqual(sentiments.dimension, 'culture')
        self.assertEqual(sentiments.wave, 'baseline')

    def test_generate_sentiment_idempotent(self):
        """Running generation twice does not duplicate entries."""
        self.survey.action_generate_sentiment()
        self.survey.action_generate_sentiment()
        sentiments = self.env['rollout.sentiment'].search([
            ('survey_input_id', '=', self.user_input.id),
        ])
        self.assertEqual(len(sentiments), 1)
