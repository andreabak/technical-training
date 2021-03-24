# -*- coding: utf-8 -*-
from odoo import api, fields, models


class Books(models.Model):
    _inherit = "product.product"

    author_ids = fields.Many2many(
        "res.partner", string="Authors", domain=[("is_author", "=", True)]
    )
    edition_date = fields.Date()
    isbn = fields.Char(string="ISBN", unique=True)
    publisher_id = fields.Many2one(
        "res.partner", string="Publisher", domain=[("is_publisher", "=", True)]
    )

    copy_ids = fields.One2many("library.copy", "book_id", string="Book Copies")
    is_book = fields.Boolean(string="Is a Book", default=False)

    rentals_ids = fields.Many2many("library.rental", compute="_get_rentals")
    rentals_count = fields.Integer(compute="_get_rentals_count")

    def _get_rentals(self):
        for record in self:
            record.rentals_ids = record.env["library.rental"].search(
                [("book_id", "=", record.id)]
            )

    @api.depends("rentals_ids")
    def _get_rentals_count(self):
        for record in self:
            record.rentals_count = len(record.rentals_ids)

    def action_view_rentals(self):
        self.ensure_one()
        rentals = self.mapped("rentals_ids")
        if rentals:
            action = self.env["ir.actions.actions"]._for_xml_id("library.rental_action")
            action["domain"] = [("id", "in", rentals.ids)]
        else:
            action = {"type": "ir.actions.act_window_close"}
        return action


class BookCopy(models.Model):
    _name = "library.copy"
    _description = "Book Copy"
    _rec_name = "reference"

    book_id = fields.Many2one(
        "product.product",
        string="Book",
        domain=[("is_book", "=", True)],
        required=True,
        ondelete="cascade",
        delegate=True,
    )
    reference = fields.Char(required=True, string="Ref")

    rental_ids = fields.One2many("library.rental", "copy_id", string="Rentals")
    book_state = fields.Selection(
        [("available", "Available"), ("rented", "Rented"), ("lost", "Lost")],
        default="available",
    )
