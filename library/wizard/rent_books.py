# -*- coding: utf-8 -*-
from odoo import fields, models


class RentBooksWizard(models.TransientModel):
    _name = "library.rent_books.wizard"
    _description = "Wizard to select books to rent"

    copy_ids = fields.Many2many("library.copy", string="Book copies", required=True)
    customer_id = fields.Many2one("res.partner", string="Customer", required=True)
    rental_ids = fields.Many2many("library.rental")
    return_date = fields.Date(required=True)

    def next_step(self):
        self.ensure_one()
        for copy in self.copy_ids:
            Rentals = self.env["library.rental"]
            values = {
                "copy_id": copy.id,
                "customer_id": self.customer_id.id,
                "return_date": self.return_date,
            }
            copy.rental_ids |= Rentals.create(values)
        action = self.env["ir.actions.actions"]._for_xml_id("library.rental_action")
        action["domain"] = [("customer_id", "=", self.customer_id.id)]
        action["target"] = "self"
        return action
