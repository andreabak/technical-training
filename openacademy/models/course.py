"""Citadel training courses model"""

from odoo import api, fields, models


class TrainingCourse(models.Model):
    _name = "openacademy.course"
    _description = "Course"

    name = fields.Char("Course Name", required=True)
    level = fields.Selection(
        [
            ("beginner", "Beginners"),
            ("intermediate", "Intermediate"),
            ("advanced", "Advanced"),
        ],
        string="Level",
    )
    description = fields.Html("Description")
