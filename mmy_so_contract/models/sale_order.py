# -*- coding: utf-8 -*-

from odoo import fields, models, _, api
from datetime import datetime


class SaleOrder(models.Model):
    _inherit = "sale.order"

    state = fields.Selection(
        selection_add=[
            ("waiting_approval", "Waiting For Approval"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
            ("sale",),
        ]
    )

    requested_approval_by = fields.Many2one(
        string="Requested Approval By",
        comodel_name="res.users",
        readonly=True,
        copy=False,
        tracking=True,
    )
    requested_approval_on = fields.Datetime(
        string="Requested Approval On",
        readonly=True,
        copy=False,
        tracking=True,
    )
    approved_by = fields.Many2one(
        string="Approved By",
        comodel_name="res.users",
        readonly=True,
        copy=False,
        tracking=True,
    )
    approved_on = fields.Datetime(
        string="Approved On",
        readonly=True,
        copy=False,
        tracking=True,
    )
    rejected_by = fields.Many2one(
        string="Rejected By",
        comodel_name="res.users",
        readonly=True,
        copy=False,
        tracking=True,
    )
    rejected_on = fields.Datetime(
        string="Rejected On",
        readonly=True,
        copy=False,
        tracking=True,
    )

    def action_request_approval(self):
        """Method to send SO for approval"""
        for rec in self.filtered(
            lambda order: order.state
            not in ["approved", "sale", "done", "cancel", "rejected"]
        ):
            rec.write(
                {
                    "state": "waiting_approval",
                    "requested_approval_by": self.env.user,
                    "requested_approval_on": datetime.now(),
                }
            )

    def action_approve(self):
        """Method to approve SO"""
        for rec in self.filtered(
            lambda order: order.state
            not in ["sale", "done", "cancel", "rejected"]
        ):
            rec.write(
                {
                    "state": "approved",
                    "approved_by": self.env.user,
                    "approved_on": datetime.now(),
                    "rejected_by": False,
                    "rejected_on": False,
                }
            )

    def action_reject(self):
        """Method to reject SO confirmation"""
        return {
            "name": "Sale Order Reject Wizard",
            "type": "ir.actions.act_window",
            "res_model": "sale.order.reject.wizard",
            "view_mode": "form",
            "view_id": self.env.ref(
                "mmy_so_contract.view_sale_order_reject_wizard_form"
            ).id,
            "target": "new",
        }

    def _action_reject(self):
        """Method to reject SO"""
        for rec in self.filtered(
            lambda order: order.state
            not in ["sale", "done", "cancel", "approved"]
        ):
            if self._context.get("message"):
                message = _(
                    "<b>Rejection Reason</b> : %s",
                    self._context.get("message"),
                )
                rec.message_post(body=message)
            rec.write(
                {
                    "state": "rejected",
                    "rejected_by": self.env.user,
                    "rejected_on": datetime.now(),
                    "approved_by": False,
                    "approved_on": False,
                }
            )

    def action_draft(self):
        """Extend method to clear approval fields if reset to draft"""
        res = super().action_draft()
        self.write(
            {
                "requested_approval_by": False,
                "requested_approval_on": False,
                "approved_by": False,
                "approved_on": False,
                "rejected_by": False,
                "rejected_on": False,
            }
        )
        return res

    @api.depends("partner_id", "date_order")
    def _compute_pricelist_id(self):
        super()._compute_pricelist_id()
        for order in self:
            price_list = self.env["product.pricelist"].search(
                [
                    ("partner_id", "in", [order.partner_id.id, False]),
                ],
            )
            for line in order.order_line:
                if line.pricelist_id not in price_list:
                    line.pricelist_id = False
            filtered_list = price_list.filtered(
                lambda rec: rec.partner_id
                and rec.effective_date
                and rec.expiration_date
                and rec.effective_date <= order.date_order
                and rec.expiration_date >= order.date_order
            )
            if (
                order.partner_id
                and order.pricelist_id
                and filtered_list
                and (order.pricelist_id != filtered_list[0])
            ):
                order.pricelist_id = filtered_list[0].id
            order._recompute_prices()

    def _can_be_confirmed(self):
        self.ensure_one()
        return self.state in {"draft", "sent", "approved"}
