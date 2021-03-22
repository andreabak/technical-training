from odoo import fields, models


class Registration(models.TransientModel):
    _name = "openacademy.wizard.registration"
    _description = "Attendees Registration Wizard"

    # def _default_session(self):
    #     return self.env['openacademy.session'].browse(self._context.get('active_id'))

    session_id = fields.Many2one("openacademy.session", string="Session", required=True)
    attendee_ids = fields.Many2many("res.partner", string="Attendees")

    def register(self):
        self.session_id.attendee_ids |= self.attendee_ids
        return {}
