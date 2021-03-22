# -*- coding: utf-8 -*-, api
from odoo import api, fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    instructor = fields.Boolean(default=False)
    session_ids = fields.Many2many(
        "openacademy.session", string="Attended Sessions", readonly=True
    )
    courses_ids = fields.Many2many(
        "openacademy.course", compute="_get_courses", store=True
    )

    level = fields.Integer(compute="_get_level", string="Level", store=True)

    @api.depends("session_ids")
    def _get_courses(self):
        for record in self:
            record.courses_ids = record.env["openacademy.course"].search(
                [("session_ids", "in", record.session_ids.ids)]
            )

    @api.depends("category_id", "category_id.name")
    def _get_level(self):
        for partner in self:
            level = []
            for categ in partner.category_id:
                if "Chain Level" in categ.name:
                    level.append(int(categ.name.split(" ")[-1]))
            partner.level = max(level) if level else 0
