# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class Course(models.Model):
    _name = "openacademy.course"
    _description = "Course"

    name = fields.Char(string="Title", required=True)
    description = fields.Text()

    responsible_id = fields.Many2one("openacademy.partner", string="Responsible")
    session_ids = fields.One2many("openacademy.session", "course_id", string="Sessions")

    level = fields.Selection(
        [("easy", "Easy"), ("medium", "Medium"), ("hard", "Hard")],
        string="Difficulty Level",
    )

    max_attendees_default = fields.Integer(
        "Default Attendees Limit",
        help="The default attendees limit that will be used on new sessions",
    )


class Session(models.Model):
    _name = "openacademy.session"
    _description = "Session"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    state = fields.Selection(
        [("draft", "Draft"), ("confirmed", "Confirmed"), ("done", "Done")],
        default="draft",
    )

    start_date = fields.Date(default=fields.Date.context_today)
    duration = fields.Float(digits=(6, 2), help="Duration in days", default=1)

    instructor_id = fields.Many2one("openacademy.partner", string="Instructor")
    course_id = fields.Many2one(
        "openacademy.course", ondelete="cascade", string="Course", required=True
    )
    attendee_ids = fields.Many2many("openacademy.partner", string="Attendees")

    max_attendees = fields.Integer(
        "Attendees Limit", compute="_get_max_attendees", inverse="_set_max_attendees"
    )
    max_attendees_course = fields.Integer(related="course_id.max_attendees_default")
    max_attendees_custom = fields.Integer()
    # FIXME: one bad side-effect of this, is that if the max attendees is changed
    #        in the course, it could invalidate sessions (also past ones) that
    #        don't have an explicit value defined.
    #        Maybe we should just use its value to populate the field here at record creation?

    @api.depends("max_attendees_custom", "max_attendees_course")
    def _get_max_attendees(self):
        for record in self:
            record.max_attendees = (
                record.max_attendees_custom or record.max_attendees_course
            )

    def _set_max_attendees(self):
        for record in self:
            if not record.max_attendees:
                continue
            record.max_attendees_custom = record.max_attendees

    # FIXME: atm there's no easy way to restore the default course-inherited limit

    @staticmethod
    def _is_attendees_over_limit(record):
        max_attendees = record.max_attendees
        return max_attendees and len(record.attendee_ids) > max_attendees

    @api.constrains("attendee_ids")
    def _check_attendees_limit(self):
        for record in self:
            if self._is_attendees_over_limit(record):
                raise ValidationError(f"Too many attendees (> {record.max_attendees})")

    @api.onchange("attendee_ids")
    def _verify_attendees_limit(self):
        for record in self:
            if self._is_attendees_over_limit(record):
                return {
                    "warning": {
                        "title": "Too many attendees",
                        "message": f"This session must have less than {record.max_attendees} attendees",
                    },
                }
