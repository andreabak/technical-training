# -*- coding: utf-8 -*-
from odoo import api, fields, models


class TaskType(models.Model):
    _name = "coopplanning.task.type"
    _description = "Task Type"

    name = fields.Char()
    description = fields.Text()

    area = fields.Char()
    active = fields.Boolean(default=True)


class TaskTemplate(models.Model):
    _name = "coopplanning.task.template"
    _description = "Task Template"

    name = fields.Char(required=True)

    day_nb_id = fields.Many2one("coopplanning.daynumber", string="Day")
    day_number = fields.Integer(related="day_nb_id.number", store=True)
    task_type_id = fields.Many2one("coopplanning.task.type", string="Task Type")
    task_type_area = fields.Char(related="task_type_id.area", store=True)

    start_time = fields.Float()
    duration = fields.Float(help="Duration in Hour")
    end_time = fields.Float(compute="_compute_end_time", store=True)
    # TODO: end_time inverse computation (setter) would be cool

    @api.depends("start_time", "duration")
    def _compute_end_time(self):
        for record in self:
            if record.start_time is None:
                record.end_time = None
            else:
                record.end_time = record.start_time + (record.duration or 0)

    worker_nb = fields.Integer(
        string="Number of worker", help="Max number of worker for this task", default=1
    )
    worker_ids = fields.Many2many(
        "coopplanning.partner", string="Recurrent worker assigned"
    )
    active = fields.Boolean(default=True)
