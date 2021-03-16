"""Cooperative workers model"""

from odoo import api, models, fields


class Worker(models.Model):  # TODO: does class name have to match extended one?
    _inherit = "hr.employee"

    # FIXME: Nothing's happening here
