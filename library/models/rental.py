# -*- coding: utf-8 -*-
from odoo import api, fields, models


class Rentals(models.Model):
    _name = "library.rental"
    _description = "Book rental"

    customer_id = fields.Many2one("res.partner", required=True, string="Customer")
    copy_id = fields.Many2one("library.copy", required=True, string="Book Copy")
    book_id = fields.Many2one(
        "product.product", string="Book", related="copy_id.book_id", readonly=True
    )
    # TODO: constraint: cannot rent a book copy that's not "available", limit domain in view

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("rented", "Rented"),
            ("returned", "Returned"),
            ("lost", "Lost"),
        ],
        default="draft",
        required=True,
    )
    # TODO: constraint: can move between states only if appropriate dates are set

    rental_date = fields.Date()
    return_date = fields.Date()

    customer_address = fields.Text(compute="_compute_customer_address")
    customer_email = fields.Char(related="customer_id.email")

    book_authors = fields.Many2many(related="copy_id.author_ids")
    book_edition_date = fields.Date(related="copy_id.edition_date")
    book_publisher = fields.Many2one(related="copy_id.publisher_id")

    rent_price = fields.Float(default=None, help="Rental price per day")
    loss_fee = fields.Float(default=None, help="Fee for lost book")
    bill_amount = fields.Float(compute="_compute_bill_amount", store=True)

    return_reminder_days = fields.Integer(default=15)
    reminders_sent_ids = fields.Many2many("mail.mail")

    # TODO: There was something about auto-moving or constraints for states in docs?

    @api.depends("customer_id")
    def _compute_customer_address(self):
        self.customer_address = self.customer_id.address_get()

    @api.depends("state", "rent_price", "loss_fee", "rental_date", "return_date")
    def _compute_bill_amount(self):
        for record in self:
            if not record.rental_date:
                bill_amount = 0
            else:
                return_date = record.return_date or fields.Date.context_today(record)
                elapsed_days = (return_date - record.rental_date).total_seconds() / (
                    24 * 60 * 60
                )
                if elapsed_days < 0:
                    elapsed_days = 0
                bill_amount = record.rent_price * elapsed_days
                if record.state == "lost":
                    bill_amount += record.loss_fee
            record.bill_amount = bill_amount

    @api.onchange("copy_id")
    def _update_prices(self):
        for record in self:
            if record._origin.book_id != record.book_id:
                record.rent_price = record.book_id.rent_price
                record.loss_fee = record.book_id.loss_fee

    def mark_rented(self):
        for record in self:
            record.write({"state": "rented"})

    def mark_returned(self):
        for record in self:
            record.write({"state": "returned"})

    def mark_lost(self):
        for record in self:
            record.write({"state": "lost"})

    def _cron_update(self):
        records = self.search([("state", "=", "rented")])  # TODO: Add filter for date?
        records._check_send_reminder()

    def _check_send_reminder(self):
        for record in self:
            newest_reminder = None
            if record.reminders_sent_ids:  # FIXME: Do this with a domain perhaps?
                for reminder in record.reminders_sent_ids:
                    if not newest_reminder or reminder.date > newest_reminder:
                        newest_reminder = reminder.date
            if not newest_reminder or (
                (fields.Datetime.now() - newest_reminder).total_seconds()
                >= record.return_reminder_days
            ):
                mail_template = self.env.ref("library.mail_template_book_return")
                mail_id = mail_template.send_mail(record.id)
                record.write({"reminders_sent_ids": [(4, mail_id)]})

    def write(self, vals):
        state_new = vals.get("state")
        if state_new:
            for record in self:
                if state_new != record.state:
                    if state_new == "rented":
                        if not vals.get("rental_date", record.rental_date):
                            record.rental_date = fields.Date.context_today(record)
                        record.copy_id.state = "rented"
                    if state_new in ("returned", "lost"):
                        if not vals.get("return_date", record.return_date):
                            record.return_date = fields.Date.context_today(record)
                    if state_new == "returned":
                        record.copy_id.state = "available"
                    if state_new == "lost":
                        record.copy_id.state = "lost"
        res = super().write(vals)
        for record in self:
            record.customer_id.recompute()
        return res
