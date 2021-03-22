# -*- coding: utf-8 -*-
from odoo import api, fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    is_author = fields.Boolean(string="Is an Author", default=False)
    is_publisher = fields.Boolean(string="Is a Publisher", default=False)

    rental_ids = fields.One2many("library.rental", "customer_id", string="Rentals")
    payment_ids = fields.One2many("library.payment", "customer_id", string="Payments")
    owed_amount = fields.Float(compute="_compute_owed_amount", store=True)

    @api.depends("rental_ids", "payment_ids")
    def _compute_owed_amount(self):
        for record in self:
            owed_amount = 0
            for rental in record.rental_ids:
                owed_amount += rental.bill_amount
            for payment in record.payment_ids:
                owed_amount -= payment.amount
            record.owed_amount = owed_amount
