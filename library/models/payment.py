from odoo import api, fields, models


class Payment(models.Model):
    _name = "library.payment"
    _description = "Payment"

    customer_id = fields.Many2one("res.partner", required=True, string="Customer")
    amount = fields.Float(required=True)
    rental_id = fields.Many2one("library.rental", string="Rental")

    def write(self, vals):
        res = super().write(vals)
        for record in self:
            record.customer_id.recompute()
        return res
