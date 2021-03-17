# -*- coding: utf-8 -*-
import math
from datetime import datetime

from odoo import api, fields, models
from pytz import UTC


def float_to_time(f):
    decimal, integer = math.modf(f)
    return "{}:{}".format(
        str(int(integer)).zfill(2),
        str(int(round(decimal * 60))).zfill(2),
    )


def floatime_to_hour_minute(f):
    decimal, integer = math.modf(f)
    return int(integer), int(round(decimal * 60))


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
    day_nb = fields.Integer(related="day_nb_id.number", store=True)
    task_type_id = fields.Many2one("coopplanning.task.type", string="Task Type")
    task_area = fields.Char(related="task_type_id.area", store=True)

    start_time = fields.Float()
    duration = fields.Float(help="Duration in Hour")
    end_time = fields.Float(
        compute="_compute_end_time", inverse="_invert_end_time", store=True
    )
    # TODO: end_time inverse computation (setter) would be cool

    worker_nb = fields.Integer(
        string="Number of worker", help="Max number of worker for this task", default=1
    )
    worker_ids = fields.Many2many(
        "coopplanning.partner", string="Recurrent worker assigned"
    )
    active = fields.Boolean(default=True)

    floating = fields.Boolean(
        "Floating Task",
        help="This task will be not assigned to someone and will be available for non recurring workers",
    )

    @api.depends("start_time", "duration")
    def _compute_end_time(self):
        for record in self:
            if record.start_time is None:
                record.end_time = None
            else:
                record.end_time = record.start_time + (record.duration or 0)

    def _invert_end_time(self):
        for record in self:
            if record.end_time is None:
                continue
            if record.start_time is None:
                if record.duration is None:
                    continue
                record.start_time = record.end_time - record.duration
            else:
                record.duration = record.end_time - record.start_time

    def generate_task(self):
        self.ensure_one()
        task = self.env["coopplanning.task"]
        today = datetime.today()
        h_begin, m_begin = floatime_to_hour_minute(self.start_time)
        h_end, m_end = floatime_to_hour_minute(self.end_time)
        for i in range(0, self.worker_nb):
            worker_id = self.worker_ids[i].id if len(self.worker_ids) > i else False
            task.create(
                {
                    "name": "{name} ({start}) - ({end}) [{i}]".format(
                        name=self.name,
                        start=float_to_time(self.start_time),
                        end=float_to_time(self.end_time),
                        i=i,
                    ),
                    "task_template_id": self.id,
                    "task_type_id": self.task_type_id.id,
                    "worker_id": worker_id,
                    "start_time": (
                        fields.Datetime.context_timestamp(self, today)
                        .replace(hour=h_begin, minute=m_begin, second=0)
                        .astimezone(UTC)
                    ),
                    "end_time": (
                        fields.Datetime.context_timestamp(self, today)
                        .replace(hour=h_end, minute=m_end, second=0)
                        .astimezone(UTC)
                    ),
                }
            )

    # Solution : Empty the field worker_ids when floating is selected to be sure no worker will be pre assigned to the task
    @api.onchange("floating")
    def _onchange_floating(self):
        if self.floating:
            self.worker_ids = self.env["res.partner"]


class Task(models.Model):
    _name = "coopplanning.task"
    _description = "Task"

    name = fields.Char()

    task_template_id = fields.Many2one("coopplanning.task.template")
    task_type_id = fields.Many2one("coopplanning.task.type", string="Task Type")

    start_time = fields.Datetime()
    end_time = fields.Datetime()

    worker_id = fields.Many2one("coopplanning.partner")
