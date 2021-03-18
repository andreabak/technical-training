# -*- coding: utf-8 -*-, api
from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_instructor = fields.Boolean(default=False)
    attended_session_ids = fields.Many2many(
        "openacademy.session", string="Attended sessions", readonly=True
    )
