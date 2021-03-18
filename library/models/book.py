# -*- coding: utf-8 -*-
from odoo import fields, models


class Books(models.Model):
    _name = "library.book"
    _description = "Book"

    name = fields.Char(string="Title")

    author_ids = fields.Many2many("library.partner", string="Authors")
    edition_date = fields.Date()
    isbn = fields.Char(string="ISBN")
    publisher_id = fields.Many2one("library.publisher", string="Publisher")

    # TODO: can we show all rented book copies from the book itself


class BookCopy(models.Model):
    _name = "library.book.copy"
    _description = "Book Copy"

    _inherits = {"library.book": "book_id"}

    book_id = fields.Many2one("library.book", "Book", required=True, ondelete="cascade")

    reference = fields.Char("Reference", required=True, index=True)
    rental_id = fields.One2many(
        "library.rental", "book_copy_id", string="Rentals", readonly=True
    )
