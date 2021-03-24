# -*- coding: utf-8 -*-
from odoo import fields, models


class City(models.Model):
    _name = "kingdom.city"
    _description = "Stats for each major city"

    name = fields.Char(required=True)
    citizen_count = fields.Integer(
        string="Number of citizen", groups="kingdom.group_economist"
    )
    production_food = fields.Float(
        string="Food production",
        help="Number of tons of production",
        groups="kingdom.group_economist",
    )
