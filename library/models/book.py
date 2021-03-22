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

    rent_price = fields.Float(help="Rental price per day")
    loss_fee_pct = fields.Float(
        "Loss Fee %", default=1.0, help="% fee for losing the book, based on its price"
    )
    loss_fee = fields.Float(compute="_compute_loss_fee", help="Fee for lost book")

    @api.depends("loss_fee_pct", "standard_price")
    def _compute_loss_fee(self):
        for book in self:
            book.loss_fee = book.standard_price * book.loss_fee_pct


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
    reference = fields.Char()

    state = fields.Selection(
        [
            ("available", "Available"),
            ("rented", "Rented"),
            ("lost", "Lost"),
        ],
        default="available",
        required=True,
    )
    active = fields.Boolean(default=True)

    rental_ids = fields.One2many("library.rental", "copy_id", string="Rentals")

    def write(self, vals):
        state_new = vals.get("state")
        if state_new == "lost":
            vals["active"] = False
        res = super().write(vals)
        return res
