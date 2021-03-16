"""Library rentals model"""

from odoo import api, models, fields


# TODO: Add to access.csv?
class Customer(models.Model):  # TODO: does class name have to match extended one?
    _inherit = "res.partner"
    # TODO: Can we have an alias like `library.customer` but actually just extend `res.partner?

    # TODO: Method that gets a list of rentals per customer to use in views


# TODO: Do we allow multiple book per single rental?
class Rental(models.Model):
    _name = "library.rental"
    _description = "Rental"

    # TODO: pick a `ondelete` strategy for both relationships
    book_id = fields.Many2one("library.book", string="Book")
    customer_id = fields.Many2one("res.partner", string="Customer")
    rent_date = fields.Datetime("Date rented", default=fields.Datetime.now)
    return_date = fields.Datetime("Date returned")

    # TODO: Validation and constraints
    #       - return date > rent date
