# -*- coding: utf-8 -*-
from odoo import fields, models


class Rentals(models.Model):
    _name = 'library.rental'
    _description = 'Book rental'

    customer_id = fields.Many2one('library.partner', string='Customer')
    customer_email = fields.Char(related="customer_id.email", readonly=True)
    customer_address = fields.Text(related="customer_id.address", readonly=True)

    book_id = fields.Many2one('library.book', string='Book')
    book_authors = fields.Many2many(related="book_id.author_ids", readonly=True)
    book_edition_date = fields.Date(related="book_id.edition_date", readonly=True)
    book_isbn = fields.Char(related="book_id.isbn", readonly=True)
    book_publisher = fields.Many2one(related="book_id.publisher_id", readonly=True)

    rental_date = fields.Date()
    return_date = fields.Date()
