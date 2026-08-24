"""Rollout Sentiment — pulse survey tracking for rollout projects."""

from odoo import models, fields, api


class RolloutSentiment(models.Model):
    _name = 'rollout.sentiment'
    _description = 'Rollout Sentiment Entry'
    _order = 'create_date desc'

    project_id = fields.Many2one(
        'rollout.project', string='Project', required=True, ondelete='cascade')
    phase_id = fields.Many2one(
        'rollout.phase', string='Phase', ondelete='set null')
    user_id = fields.Many2one(
        'res.users', string='User', required=True,
        default=lambda self: self.env.user)
    score = fields.Integer('Score (1-5)', required=True)
    comment = fields.Text('Comment')

    # Hotspot detection (manual or AI-assisted)
    hotspot_detected = fields.Boolean('Hotspot Detected')
    hotspot_department = fields.Char('Hotspot Department')
    hotspot_topic = fields.Char('Hotspot Topic')
    hotspot_confidence = fields.Float('Hotspot Confidence')

    _sql_constraints = [
        ('check_score_range', 'CHECK(score >= 1 AND score <= 5)',
         'Score must be between 1 and 5'),
    ]

    @api.model
    def get_phase_sentiment(self, phase_id):
        """Return average sentiment for a phase."""
        entries = self.search([('phase_id', '=', phase_id)])
        if not entries:
            return None
        return sum(e.score for e in entries) / len(entries)

    @api.model
    def get_project_trend(self, project_id):
        """Return sentiment trend for a project (latest avg - previous avg)."""
        entries = self.search(
            [('project_id', '=', project_id)], order='create_date')
        if len(entries) < 2:
            return 0.0
        mid = len(entries) // 2
        first = entries[:mid]
        second = entries[mid:]
        first_avg = sum(e.score for e in first) / len(first)
        second_avg = sum(e.score for e in second) / len(second)
        return round(second_avg - first_avg, 2)
