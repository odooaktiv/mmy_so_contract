# -*- coding: utf-8 -*-

from odoo import models, fields


class SaleRejectWizard(models.TransientModel):
    _name = "sale.order.reject.wizard"
    _description = "Sale Order Reject Wizard"

    reject_reason = fields.Char(string="Reject Reason", required=1)

    def action_confirm(self):
        if self._context.get("active_id"):
            order = self.env["sale.order"].browse(
                self._context.get("active_id")
            )
            order.with_context(message=self.reject_reason)._action_reject()
        return {"type": "ir.actions.act_window_close"}
