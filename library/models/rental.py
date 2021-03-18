# -*- coding: utf-8 -*-
from odoo import fields, models


class Rentals(models.Model):
    _name = "library.rental"
    _description = "Book rental"

    customer_id = fields.Many2one("library.partner", string="Customer", required=True)
    book_copy_id = fields.Many2one(
        "library.book.copy", string="Book Copy", required=True
    )
    # TODO: Unique constraints for book copies not returned

    rental_date = fields.Date()
    return_date = fields.Date()

    customer_address = fields.Text(related="customer_id.address")
    customer_email = fields.Char(related="customer_id.email")

    book_authors = fields.Many2many(related="book_copy_id.author_ids")
    book_edition_date = fields.Date(related="book_copy_id.edition_date")
    book_publisher = fields.Many2one(related="book_copy_id.publisher_id")
