"""Cooperative tasks model"""

from odoo import api, models, fields


class Task(models.Model):
    _name = "coopplanning.task"

    name = fields.Char("Name")
    description = fields.Html("Description")
    type = fields.Selection(
        [
            ("oneshot", "One-Shot"),
            ("recurring", "Recurring task"),
        ],
        string="Type",
    )
    active = fields.Boolean(
        "Active",
        default=True,
        help="Whether the task is active or not (ie. done/archived)",
    )
    due_date = fields.Date("Due Date")
    # TODO: Perhaps merge with task_type? Perhaps not.
    recurring_type = fields.Selection(
        [
            ("days", "Day(s)"),
            ("weeks", "Week(s)"),
            ("months", "Month(s)"),
        ],
        string="Recurring interval type",
    )
    recurring_interval = fields.Integer("Recurring interval amount")
    time_demand = fields.Float(
        "Time Demand", help="The time (per worker) the task requires to be done"
    )
    workers_required = fields.Integer(
        "Workers Required", help="How many workers are required to do this task"
    )
    assignees_ids = fields.Many2many(
        "hr.employee", string="Assignees", help="Workers assigned to this task"
    )

    # TODO: This solution feels by no means complete. There's only one instance
    #       of the task that persists over time, no matter if it's a recurring
    #       one or a one-shot. Basically we have no history.
    #       This could be perhaps better implemented by having a sort of "TaskDefinition"
    #       model from which actual single-occurrence tasks are created?
    #       Or maybe there's a way to periodically automate tasks duplication
    #       for recurring ones.

    # TODO: Add constraints and validation
