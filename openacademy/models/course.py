# -*- coding: utf-8 -*-
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

    @api.depends("session_ids")
    def _compute_session_count(self):
        for course in self:
            course.session_count = len(course.session_ids)


class Session(models.Model):
    _name = "openacademy.session"
    _inherit = ["mail.thread"]
    _description = "Session"

    name = fields.Char(required=True)
    description = fields.Html()
    active = fields.Boolean(default=True)
    state = fields.Selection(
        [
            ("draft", "In preparation"),
            ("ready", "Ready"),
            ("confirmed", "Confirmed"),
            ("done", "Done"),
        ],
        default="draft",
        tracking=True,
    )
    level = fields.Selection(related="course_id.level", readonly=True)
    responsible_id = fields.Many2one(
        related="course_id.responsible_id", readonly=True, store=True
    )

    start_date = fields.Date(default=fields.Date.context_today, tracking=True)
    end_date = fields.Date(default=fields.Date.today, tracking=True)
    duration = fields.Float(digits=(6, 2), help="Duration in days", default=1)

    instructor_id = fields.Many2one("res.partner", string="Instructor")
    course_id = fields.Many2one(
        "openacademy.course", ondelete="cascade", string="Course", required=True
    )
    attendee_ids = fields.Many2many("res.partner", string="Attendees", tracking=True)
    attendees_count = fields.Integer(compute="_get_attendees_count", store=True)
    seats = fields.Integer(tracking=True)
    taken_seats = fields.Float(compute="_compute_taken_seats", store=True)
    autoconfirm_threshold = fields.Integer(default=50, tracking=True)

    def _update_followers(self, new, old=None, record=None):
        if record is None:
            record = self
        if old is None:
            old = []
        followers_before = set(old)
        followers_after = set(new)
        to_unsubscribe = followers_before - followers_after
        to_subscribe = followers_after - followers_before
        if to_unsubscribe:
            record.message_unsubscribe(list(to_unsubscribe))
        if to_subscribe:
            record.message_subscribe(list(to_subscribe))

    @api.model
    def create(self, vals_list):
        res = super().create(vals_list)
        self._update_followers(
            new=(res.responsible_id.id, res.instructor_id.id, *res.attendee_ids.ids),
            record=res,
        )
        return res

    def write(self, vals):
        attendee_ids_before = self.attendee_ids.ids
        res = super().write(vals)
        # FIXME: Only attendees get unsubbed if removed. Is this okay?
        self._update_followers(
            new=(self.responsible_id.id, self.instructor_id.id, *self.attendee_ids.ids),
            old=attendee_ids_before,
        )
        return res

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

    @api.onchange("taken_seats")
    def _autoconfirm_trigger(self):
        for session in self:
            if (
                session.autoconfirm_threshold is not None
                and session.state == "ready"
                and session.taken_seats >= session.autoconfirm_threshold
            ):
                session.state = "confirmed"

    @api.onchange("start_date", "end_date")
    def _compute_duration(self):
        if not (self.start_date and self.end_date):
            return
        if self.end_date < self.start_date:
            return {
                "warning": {
                    "title": "Incorrect date value",
                    "message": "End date is earlier then start date",
                }
            }
        delta = fields.Date.from_string(self.end_date) - fields.Date.from_string(
            self.start_date
        )
        self.duration = delta.days + 1
