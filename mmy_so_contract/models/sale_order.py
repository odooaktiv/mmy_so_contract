# -*- coding: utf-8 -*-

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    state = fields.Selection(
        selection_add=[
            ("waiting_approval", "Waiting For Approval"),
            ("approved", "Approved"),
            ("sale",),
        ]
    )

    def action_request_approval(self):
        """Method to send SO for approval"""
        for rec in self.filtered(
            lambda order: order.state
            not in ["approved", "sale", "done", "cancel"]
        ):
            rec.state = "waiting_approval"

    def action_approve(self):
        """Method to approve SO"""
        for rec in self.filtered(
            lambda order: order.state not in ["sale", "done", "cancel"]
        ):
            rec.state = "approved"
