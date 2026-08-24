"""Tests for OBMS dimension/wave snapshot on rollout.sentiment."""

from odoo.tests import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestSentimentSnapshot(TransactionCase):

    def setUp(self):
        super().setUp()
        self.customer = self.env['res.partner'].create({
            'name': 'Snapshot Test Customer',
            'is_company': True,
        })
        self.project = self.env['rollout.project'].create({
            'name': 'Snapshot Test Project',
            'customer_id': self.customer.id,
            'planning_mode': 'forward',
            'date_start': '2026-01-01',
        })
        self.sentiment = self.env['rollout.sentiment']

    def _add(self, score, dimension, wave):
        self.sentiment.create({
            'project_id': self.project.id,
            'user_id': self.env.user.id,
            'score': score,
            'dimension': dimension,
            'wave': wave,
        })

    def test_obms_snapshot_baseline(self):
        self._add(2, 'structure', 'baseline')
        self._add(4, 'structure', 'baseline')
        self._add(3, 'culture', 'baseline')
        self._add(5, 'culture', 'baseline')
        self._add(3, 'behavior', 'baseline')
        snapshot = self.sentiment.get_obms_snapshot(self.project.id, 'baseline')
        self.assertEqual(snapshot['structure'], 3.0)
        self.assertEqual(snapshot['culture'], 4.0)
        self.assertEqual(snapshot['behavior'], 3.0)

    def test_obms_snapshot_wave_filtered(self):
        self._add(2, 'structure', 'baseline')
        self._add(4, 'structure', 'midline')
        # Only midline structure is returned when wave='midline'
        self.assertEqual(
            self.sentiment.get_dimension_average(
                self.project.id, 'structure', 'midline'), 4.0)
        self.assertEqual(
            self.sentiment.get_dimension_average(
                self.project.id, 'culture', 'midline'), None)
