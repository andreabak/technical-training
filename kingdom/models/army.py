# -*- coding: utf-8 -*-
from odoo import api, fields, models


class Army(models.Model):
    _name = "kingdom.army"
    _description = "Armies"

    commander = fields.Many2one("res.users")
    can_edit_commander = fields.Boolean(compute="_compute_can_edit_commander")

    infantry_count = fields.Integer(
        string="Number of infantry units", groups="kingdom.group_commander"
    )
    cavalry_count = fields.Integer(
        string="Number of cavalry units", groups="kingdom.group_commander"
    )

    @api.depends("commander")
    def _compute_can_edit_commander(self):
        self.can_edit_responsible = self.env.user.has_group("kingdom.group_king")
