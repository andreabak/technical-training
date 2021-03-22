# -*- coding: utf-8 -*-
from datetime import timedelta

from odoo import api, exceptions, fields, models


class Course(models.Model):
    _name = "openacademy.course"
    _description = "Course"

    name = fields.Char(string="Title", required=True)
    description = fields.Text()

    responsible_id = fields.Many2one(
        "res.users", ondelete="set null", string="Responsible"
    )
    session_ids = fields.One2many("openacademy.session", "course_id", string="Sessions")

    level = fields.Selection(
        [("easy", "Easy"), ("medium", "Medium"), ("hard", "Hard")],
        string="Difficulty Level",
    )
    session_count = fields.Integer(compute="_compute_session_count")

    attendees_ids = fields.Many2many(
        "res.partner", compute="_get_attendees", store=True
    )
    attendees_count = fields.Integer(compute="_get_attendees_count")

    _sql_constraints = [
        (
            "name_description_check",
            "CHECK(name != description)",
            "The title of the course should not be the description",
        ),
        ("name_unique", "UNIQUE(name)", "The course title must be unique"),
    ]

    def copy(self, default=None):
        default = dict(default or {})

        copied_count = self.search_count(
            [("name", "=like", u"Copy of {}%".format(self.name))]
        )
        if not copied_count:
            new_name = u"Copy of {}".format(self.name)
        else:
            new_name = u"Copy of {} ({})".format(self.name, copied_count)

        default["name"] = new_name
        return super(Course, self).copy(default)

    @api.depends("session_ids")
    def _compute_session_count(self):
        for course in self:
            course.session_count = len(course.session_ids)

    @api.depends("session_ids")
    def _get_attendees(self):
        for record in self:
            record.attendees_ids = record.env["res.partner"].search(
                [("session_ids", "in", record.session_ids.ids)]
            )

    @api.depends("attendees_ids")
    def _get_attendees_count(self):
        for record in self:
            record.attendees_count = len(record.attendees_ids)

    def action_view_attendees(self):
        attendees = self.mapped("attendees_ids")
        if attendees:
            action = self.env["ir.actions.actions"]._for_xml_id(
                "openacademy.partner_action"
            )
            action["domain"] = [("id", "in", attendees.ids)]
        else:
            action = {"type": "ir.actions.act_window_close"}
        return action


class Session(models.Model):
    _name = "openacademy.session"
    _inherit = ["mail.thread"]
    _order = "name"
    _description = "Session"

    name = fields.Char(required=True)
    description = fields.Html()
    active = fields.Boolean(default=True)
    state = fields.Selection(
        [("draft", "Draft"), ("confirmed", "Confirmed"), ("done", "Done")],
        default="draft",
    )
    level = fields.Selection(related="course_id.level", readonly=True)
    responsible_id = fields.Many2one(
        related="course_id.responsible_id", readonly=True, store=True
    )

    start_date = fields.Date(default=fields.Date.context_today)
    end_date = fields.Date(
        string="End date", store=True, compute="_get_end_date", inverse="_set_end_date"
    )
    duration = fields.Float(digits=(6, 2), help="Duration in days", default=1)

    instructor_id = fields.Many2one("res.partner", string="Instructor")
    course_id = fields.Many2one(
        "openacademy.course", ondelete="cascade", string="Course", required=True
    )
    attendee_ids = fields.Many2many("res.partner", string="Attendees")
    attendees_count = fields.Integer(compute="_get_attendees_count", store=True)
    seats = fields.Integer()
    taken_seats = fields.Float(compute="_compute_taken_seats", store=True)
    percentage_per_day = fields.Integer("%", default=100)

    def _warning(self, title, message):
        return {
            "warning": {
                "title": title,
                "message": message,
            }
        }

    @api.depends("seats", "attendee_ids")
    def _compute_taken_seats(self):
        for session in self:
            if not session.seats:
                session.taken_seats = 0.0
            else:
                session.taken_seats = 100.0 * len(session.attendee_ids) / session.seats

    @api.depends("attendee_ids")
    def _get_attendees_count(self):
        for session in self:
            session.attendees_count = len(session.attendee_ids)

    @api.onchange("seats", "attendee_ids")
    def _verify_valid_seats(self):
        if self.seats < 0:
            return self._warning(
                "Incorrect 'seats' value",
                "The number of available seats may not be negative",
            )
        if self.seats < len(self.attendee_ids):
            return self._warning(
                "Too many attendees", "Increase seats or remove excess attendees"
            )

    @api.constrains("instructor_id", "attendee_ids")
    def _check_instructor_not_in_attendees(self):
        for session in self:
            if session.instructor_id and session.instructor_id in session.attendee_ids:
                raise exceptions.ValidationError(
                    "A session's instructor can't be an attendee"
                )

    @api.depends("start_date", "duration")
    def _get_end_date(self):
        for session in self:
            if not (session.start_date and session.duration):
                session.end_date = session.start_date
            else:
                # Add duration to start_date, but: Monday + 5 days = Saturday,
                # so subtract one second to get on Friday instead
                start = fields.Datetime.from_string(session.start_date)
                duration = timedelta(days=session.duration, seconds=-1)
                session.end_date = str(start + duration)

    def _set_end_date(self):
        for session in self:
            if session.start_date and session.end_date:
                # Compute the difference between dates, but: Friday - Monday = 4
                # days, so add one day to get 5 days instead
                start_date = fields.Datetime.from_string(session.start_date)
                end_date = fields.Datetime.from_string(session.end_date)
                session.duration = (end_date - start_date).days + 1

    def action_draft(self):
        for rec in self:
            rec.state = "draft"
            rec.message_post(
                body="Session %s of the course %s reset to draft"
                % (rec.name, rec.course_id.name)
            )

    def action_confirm(self):
        for rec in self:
            rec.state = "confirmed"
            rec.message_post(
                body="Session %s of the course %s confirmed"
                % (rec.name, rec.course_id.name)
            )

    def action_done(self):
        for rec in self:
            rec.state = "done"
            rec.message_post(
                body="Session {} of the course {} done".format(
                    rec.name, rec.course_id.name
                )
            )

    def _auto_transition(self):
        for rec in self:
            if rec.taken_seats >= 50.0 and rec.state == "draft":
                rec.action_confirm()

    def write(self, vals):
        res = super(Session, self).write(vals)
        for rec in self:
            rec._auto_transition()
        if vals.get("instructor_id"):
            self.message_subscribe([vals["instructor_id"]])
        return res

    @api.model
    def create(self, vals):
        res = super(Session, self).create(vals)
        res._auto_transition()
        if vals.get("instructor_id"):
            res.message_subscribe([vals["instructor_id"]])
        return res
