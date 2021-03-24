from odoo import api, models


class TaskReport(models.AbstractModel):
    _name = "report.coopplanning.report_tasks"
    _description = "Tasks Report"

    @api.model
    def _get_report_values(self, docids, data=None):
        tasks = self.env["coopplanning.task"].browse(docids)
        workers = self.env["res.partner"].search([("task_ids", "in", tasks.ids)])
        return {
            "data": data,
            "doc_ids": tasks.ids,
            "doc_model": "res.partner",
            "docs": tasks,
            "workers": workers,
        }
