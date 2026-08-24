"""Rollout Plan Review — multi-dimensional plan review with scoring criteria."""

from odoo import models, fields, api


class RolloutPlanReview(models.Model):
    _name = 'rollout.plan.review'
    _description = 'Rollout Plan Review'
    _inherit = ['mail.thread']
    _order = 'review_date desc, id'

    project_id = fields.Many2one(
        'rollout.project', string='Project', required=True, ondelete='cascade')
    review_date = fields.Date(
        'Review Date', default=fields.Date.context_today, required=True)
    reviewer_id = fields.Many2one(
        'res.users', string='Reviewer',
        default=lambda self: self.env.user)

    overall_score = fields.Float(
        'Overall Score', compute='_compute_overall_score', store=True)

    criteria_score_ids = fields.One2many(
        'rollout.plan.review.criteria.score',
        'review_id', string='Criteria Scores')

    @api.depends('criteria_score_ids.score')
    def _compute_overall_score(self):
        for review in self:
            scores = review.criteria_score_ids.mapped('score')
            review.overall_score = (
                sum(scores) / len(scores) if scores else 0.0)


class RolloutPlanReviewCriteria(models.Model):
    _name = 'rollout.plan.review.criteria'
    _description = 'Plan Review Criteria'
    _order = 'dimension, sequence'

    name = fields.Char('Criterion', required=True, translate=True)
    dimension = fields.Selection([
        ('scope', 'Scope & Objectives'),
        ('stakeholder', 'Stakeholder Engagement'),
        ('communication', 'Communication'),
        ('competency', 'Competency & Training'),
        ('risk', 'Risk Management'),
        ('timeline', 'Timeline & Resources'),
        ('change', 'Change Management'),
        ('measurement', 'Measurement & KPIs'),
        ('sponsorship', 'Sponsorship & Governance'),
    ], required=True, string='Dimension')
    sequence = fields.Integer('Sequence', default=10)
    description = fields.Text('Description', translate=True)
    max_score = fields.Integer('Max Score', default=5)


class RolloutPlanReviewCriteriaScore(models.Model):
    _name = 'rollout.plan.review.criteria.score'
    _description = 'Plan Review Criteria Score'

    review_id = fields.Many2one(
        'rollout.plan.review', required=True, ondelete='cascade')
    criteria_id = fields.Many2one(
        'rollout.plan.review.criteria', required=True, string='Criterion')
    score = fields.Integer(
        'Score', required=True, default=0)
    justification = fields.Text('Justification')
    ai_suggested = fields.Boolean('AI Suggested')
    ai_suggestion = fields.Integer('AI Suggestion Score')
    ai_confidence = fields.Float('AI Confidence')
