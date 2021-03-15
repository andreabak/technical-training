"""Citadel training sessions model"""

from odoo import api, fields, models


class TrainingSession(models.Model):
    _name = "openacademy.session"
    _description = "Session"

    name = fields.Char("Session Name", required=True)
    state = fields.Selection(
        selection=[
            ("draft", "In Preparation"),
            ("ongoing", "Ongoing"),
            ("ended", "Ended"),
        ],
        string="Session Stage",
        default="draft",
        required=True,
    )
    course_id = fields.Many2one(
        "training.course", ondelete="cascade", string="Course", required=True
    )
    teacher_id = fields.Many2one("res.partner", string="Teacher", required=True)
    start_date = fields.Date("Start Date")
    end_date = fields.Date("End Date")
    attendees_ids = fields.Many2many("res.partner", string="Attendees")

    # TODO: Do we add indices manually? Or does the ORM do some magic stuff?
    # TODO: Re-consider which fields have to (or not) be required
    # TODO: More constraints:
    #       - cannot have same teacher for same course for overlapping periods
    #       - end_date cannot be < start_date. Maybe convert to start_date + duration (int)?
    #       - teacher cannot be attendee (doesn't make sense)
