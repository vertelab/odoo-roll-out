"""Extend rollout.project with external-specific fields and methods."""

from odoo import models, fields, api, _


class RolloutProject(models.Model):
    _inherit = 'rollout.project'

    # Internal notes visible only to consultants
    internal_notes = fields.Text('Internal Notes')
    recommendation = fields.Text('Customer Recommendations')

    def _get_migration_data(self):
        """Serialize project data for migration to customer instance."""
        self.ensure_one()
        data = {
            'project': {
                'name': self.name,
                'planning_mode': self.planning_mode,
                'date_start': str(self.date_start) if self.date_start else None,
                'date_launch': str(self.date_launch) if self.date_launch else None,
                'perspective': 'internal',
                'migration_state': 'imported',
                'migrated_from': self.env.company.name,
                'migrated_at': fields.Datetime.now().isoformat(),
            },
            'phases': [],
            'competency_targets': [],
            'roles': [],
            'risks': [],
            'sentiments': [],
            'org_changes': [],
            'scenarios': [],
            'plan_reviews': [],
        }

        # AI settings (only present when rollout_ai is installed on the
        # external instance — otherwise the internal side falls back to defaults)
        if 'goal_sync_frequency' in self._fields:
            data['project'].update({
                'executive_summary_frequency': self.executive_summary_frequency,
                'goal_sync_frequency': self.goal_sync_frequency,
                'goal_auto_create': self.goal_auto_create,
                'goal_require_pm_approval': self.goal_require_pm_approval,
                'goal_notify_on_create': self.goal_notify_on_create,
            })

        for phase in self.phase_ids:
            data['phases'].append({
                'name': phase.name,
                'adkar_phase': phase.adkar_phase,
                'sequence': phase.sequence,
                'duration_days': phase.duration_days,
                'gate_type': phase.gate_type,
                'gate_metric': phase.gate_metric,
            })

        for target in self.competency_target_ids:
            data['competency_targets'].append({
                'name': target.name,
                'target_count': target.target_count,
                'deadline': str(target.deadline) if target.deadline else None,
                'level': target.level,
            })

        for role in self.role_ids:
            data['roles'].append({
                'name': role.name,
                'description': role.description,
            })

        for risk in self.risk_ids:
            data['risks'].append({
                'name': risk.name,
                'description': risk.description,
                'probability': risk.probability,
                'impact': risk.impact,
                'mitigation': risk.mitigation,
                'trigger_event': risk.trigger_event,
                'state': risk.state,
            })

        for sent in self.sentiment_ids:
            data['sentiments'].append({
                'score': sent.score,
                'comment': sent.comment,
                'create_date': str(sent.create_date),
            })

        for org in self.org_change_ids:
            data['org_changes'].append({
                'name': org.name,
                'change_type': org.change_type,
                'description': org.description,
                'state': org.state,
            })

        for scenario in self.scenario_ids.filtered(lambda s: s.selected):
            data['scenarios'].append({
                'name': scenario.name,
                'description': scenario.description,
                'risk_level': scenario.risk_level,
                'adoption_estimate': scenario.adoption_estimate,
            })

        for review in self.plan_review_ids:
            review_data = {'review_date': str(review.review_date), 'scores': []}
            for score in review.criteria_score_ids:
                review_data['scores'].append({
                    'criteria_name': score.criteria_id.name,
                    'score': score.score,
                    'justification': score.justification,
                })
            data['plan_reviews'].append(review_data)

        return data
