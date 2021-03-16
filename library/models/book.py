"""Library books model"""

from odoo import api, models, fields


# TODO: Add to access.csv?
class BookIndustryPerson(models.Model):  # FIXME: Ugly ass name
    """
    Represents a person working in the book industry, like author, editor, etc.
    Inherits from `res.partner` creating a new model instead of extending.
    """

    # TODO: It would have been nice to inherit from "res.partner", but it seems
    #       that model is too bloated, and some other inherits (like mail channels)
    #       create conflicts with m2m rel tables.

    _name = "library.bookindustryperson"
    _description = "Book Industry Person"  # FIXME: Find better name

    name = fields.Char("Name")

    # I've decided to let the book relationships decide whether they'll be authors,
    # editors, etc., rather than using an explicit field to define it.
    # TODO: Reconsider?


class Book(models.Model):
    # TODO: Should this be a product? Stockable with finite quantity?
    _name = "library.book"
    _description = "Book"

    title = fields.Char("Title")
    authors_ids = fields.Many2many(
        "library.bookindustryperson",
        "library_book_author_rel",
        string="Authors",
    )
    editors_ids = fields.Many2many(
        "library.bookindustryperson",
        "library_book_editor_rel",
        string="Editors",
    )
    isbn = fields.Char("ISBN")  # TODO: Validation
    edition_date = fields.Date("Edition Date")
    edition_year = fields.Integer("Edition Year", compute="_get_edition_year")
    # TODO: Add setter and search functions to edition year

    @api.depends("edition_date")
    def _get_edition_year(self):
        for record in self:
            record.edition_year = record.edition_date.year
