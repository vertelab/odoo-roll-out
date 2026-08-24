"""Rollout Portfolio — manage multiple parallel rollout projects."""

from odoo import models, fields, api


class RolloutPortfolio(models.Model):
    _name = 'rollout.portfolio'
    _description = 'Rollout Portfolio'

    name = fields.Char('Portfolio Name', required=True)
    project_ids = fields.Many2many(
        'rollout.project', string='Projects')
    manager_id = fields.Many2one(
        'res.users', string='Portfolio Manager')

    # Computed metrics across all projects
    active_project_count = fields.Integer(
        'Active Projects', compute='_compute_metrics')
    total_competency_gap = fields.Integer(
        'Total Gap', compute='_compute_metrics')
    avg_sentiment = fields.Float(
        'Average Sentiment', compute='_compute_metrics')
    total_risk_score = fields.Integer(
        'Total Risk', compute='_compute_metrics')

    @api.depends('project_ids', 'project_ids.state',
                 'project_ids.total_competency_gap',
                 'project_ids.total_risk_score')
    def _compute_metrics(self):
        for portfolio in self:
            projects = portfolio.project_ids
            portfolio.active_project_count = len(
                projects.filtered(lambda p: p.state == 'active'))
            portfolio.total_competency_gap = sum(
                p.total_competency_gap for p in projects)
            portfolio.total_risk_score = sum(
                p.total_risk_score for p in projects)
            # Average sentiment across projects with entries
            sentiments = [
                p.sentiment_ids.sorted('create_date')[-1:].score
                for p in projects if p.sentiment_ids
            ]
            scores = [s[0] for s in sentiments if s]
            portfolio.avg_sentiment = (
                sum(scores) / len(scores) if scores else 0.0)
