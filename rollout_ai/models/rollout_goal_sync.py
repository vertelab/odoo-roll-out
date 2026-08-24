"""Goal Sync — bridge between rollout.competency.target and ai.personal.goal."""

import logging

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class RolloutGoalSync(models.AbstractModel):
    _name = 'rollout.goal.sync'
    _description = 'Sync rollout competency targets to ai.personal.goal'

    @api.model
    def _find_employees_below_target(self, target):
        """Find employees assigned to the target's role who are below the target level.

        Returns a recordset of hr.employee (or empty).
        """
        if not target.role_id:
            return self.env['hr.employee']

        employees = target.role_id.employee_ids
        if not employees:
            return self.env['hr.employee']

        # Check existing ai.personal.goal to avoid duplicates
        existing_goal_employees = self.env['ai.personal.goal'].search([
            ('source', '=', 'rollout'),
            ('source_ref', '=', f'rollout.competency.target,{target.id}'),
            ('status', 'in', ['proposed', 'active']),
        ]).mapped('user_id.employee_id')

        return employees - existing_goal_employees

    @api.model
    def _create_smart_goal_from_target(self, target, employee):
        """Create an ai.personal.goal with SMART fields populated from a competency target.

        Returns the created goal or None.
        """
        if not hasattr(self.env, 'ai.personal.goal'):
            _logger.warning("rollout_ai: ai.personal.goal not available")
            return None

        project = target.project_id
        user = employee.user_id
        if not user:
            return None

        skill_name = target.skill_id.name or target.name
        level = target.level or 'target level'

        # Generate SMART fields
        specific = (
            f'Uppnå {skill_name} på nivå {level} '
            f'enligt rollen {target.role_id.name} i {project.name}'
        )

        return self.env['ai.personal.goal'].create({
            'user_id': user.id,
            'quest_id': user.personal_quest_id.id if user.personal_quest_id else False,
            'name': f'{skill_name} — {level}',
            'description': (
                f'Detta mål är kopplat till rollout-projektet {project.name}.\n'
                f'Roll: {target.role_id.name}\n'
                f'Deadline: {target.deadline}'
            ),
            'specific': specific,
            'measurable': f'Nå nivå {level} i {skill_name}',
            'achievable': 'Uppskattad insats: 2-4 timmar/vecka under projekttiden',
            'relevant': f'Krävs för din roll som {target.role_id.name} i rollout-projektet',
            'time_bound': target.deadline,
            'source': 'rollout',
            'source_ref': f'rollout.competency.target,{target.id}',
            'status': 'proposed',
            'category': 'skill',
        })

    @api.model
    def cron_rollout_goal_sync(self):
        """Cron: sync competency targets to personal goals for all active projects.

        Respects per-project goal sync settings (frequency, auto_create, etc.).
        """
        today = fields.Date.today()
        projects = self.env['rollout.project'].search([('state', '=', 'active')])

        for project in projects:
            # Check frequency
            freq = project.goal_sync_frequency or 'weekly'
            if freq == 'realtime':
                pass  # Always run
            elif freq == 'daily':
                pass  # Always run (cron runs daily)
            elif freq == 'weekly' and today.weekday() != 0:
                continue
            elif freq == 'manual':
                continue

            syncer = self.env['rollout.goal.sync']
            targets = project.competency_target_ids.filtered(
                lambda t: t.state in ('planned', 'in_progress', 'at_risk'))

            for target in targets:
                employees = syncer._find_employees_below_target(target)
                if not employees:
                    continue

                for employee in employees:
                    if project.goal_auto_create:
                        goal = syncer._create_smart_goal_from_target(target, employee)
                        if goal and project.goal_notify_on_create:
                            self._nudge_goal_created(employee.user_id, goal, project)
                    elif project.goal_require_pm_approval:
                        # Log suggestion for PM review
                        project.message_post(
                            body=_(
                                'Goal suggestion: %(employee)s → %(target)s',
                                employee=employee.name, target=target.name))
                    else:
                        # Create as proposed, no notification
                        syncer._create_smart_goal_from_target(target, employee)

    def _nudge_goal_created(self, user, goal, project):
        """Notify user that a new personal goal has been created for them."""
        if not user:
            return
        self.env['bus.bus']._sendone(
            user.partner_id,
            'simple_notification',
            {
                'title': 'Nytt kompetensmål',
                'message': (
                    f'🎯 Rollout {project.name}: '
                    f'Ett nytt kompetensmål har skapats för dig — {goal.name}. '
                    f'Acceptera eller justera.'),
                'sticky': True,
            }
        )


class AIPersonalGoal(models.Model):
    _inherit = 'ai.personal.goal'

    linked_rollout_target_id = fields.Many2one(
        'rollout.competency.target', string='Linked Rollout Target',
        readonly=True, ondelete='set null')

    @api.model
    def write(self, vals):
        res = super().write(vals)
        if 'status' in vals and vals['status'] == 'completed':
            for goal in self:
                if goal.source == 'rollout' and goal.linked_rollout_target_id:
                    goal.linked_rollout_target_id._recalculate_current_count()
        return res


class RolloutCompetencyTarget(models.Model):
    _inherit = 'rollout.competency.target'

    def _recalculate_current_count(self):
        """Recalculate current_count based on completed personal goals."""
        for target in self:
            completed_goals = self.env['ai.personal.goal'].search_count([
                ('source', '=', 'rollout'),
                ('source_ref', '=', f'rollout.competency.target,{target.id}'),
                ('status', '=', 'completed'),
            ])
            target.current_count = completed_goals
            # Recompute gap and state
            target._compute_gap()
            target._compute_state()

            if target.gap <= 0 and target.state != 'achieved':
                target.state = 'achieved'
                # Cancel pending goals
                pending_goals = self.env['ai.personal.goal'].search([
                    ('source', '=', 'rollout'),
                    ('source_ref', '=', f'rollout.competency.target,{target.id}'),
                    ('status', '=', 'proposed'),
                ])
                pending_goals.write({'status': 'cancelled'})
