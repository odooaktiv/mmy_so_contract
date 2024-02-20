# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    pricelist_id = fields.Many2one(
        string="Contract", comodel_name="product.pricelist"
    )

    pricelist_ids = fields.Many2many(
        "product.pricelist",
        "pricelist_product_rel",
        "pricelist_product_id",
        "pricelist_id",
        string="Pricelist",
        compute="_compute_product_pricelists",
        store=True,
    )

    @api.depends(
        "product_id",
        "product_uom",
        "product_uom_qty",
        "pricelist_id",
        "order_id.pricelist_id",
    )
    def _compute_product_pricelists(self):
        for order_line in self:
            if order_line.product_id:
                pricelist_item_id = (
                    self.env["product.pricelist.item"]
                    .sudo()
                    .search(
                        [
                            ("product_id", "=", order_line.product_id.id),
                            (
                                "pricelist_id.effective_date",
                                "<=",
                                order_line.order_id.date_order,
                            ),
                            (
                                "pricelist_id.expiration_date",
                                ">=",
                                order_line.order_id.date_order,
                            ),
                            ("date_end", ">=", order_line.order_id.date_order),
                        ]
                    )
                )
                pricelist_id = pricelist_item_id.pricelist_id.ids
                order_line.pricelist_ids = [(6, 0, pricelist_id)]

    @api.depends(
        "product_id",
        "product_uom",
        "product_uom_qty",
        "pricelist_id",
        "order_id.pricelist_id",
    )
    def _compute_pricelist_item_id(self):
        """Overwrite method to get price based on SOl's connected pricelist"""
        for line in self:
            if (
                not line.product_id
                or line.display_type
                or (not line.pricelist_id and not line.order_id.pricelist_id)
            ):
                line.pricelist_item_id = False
            else:
                pricelist = line.pricelist_id or line.order_id.pricelist_id
                line.pricelist_item_id = pricelist._get_product_rule(
                    line.product_id,
                    line.product_uom_qty or 1.0,
                    uom=line.product_uom,
                    date=line.order_id.date_order,
                )

    @api.depends(
        "product_id",
        "product_uom",
        "product_uom_qty",
        "pricelist_id",
        "order_id.pricelist_id",
    )
    def _compute_price_unit(self):
        """Add pricelist id in dependencies"""
        return super()._compute_price_unit()

    @api.onchange("product_template_id", "product_id")
    def _onchange_pricelist_id(self):
        for order_line in self:
            pricelist_item_id = (
                self.env["product.pricelist.item"]
                .sudo()
                .search(
                    [
                        ("product_id", "=", order_line.product_id.id),
                        (
                            "pricelist_id.effective_date",
                            "<=",
                            order_line.order_id.date_order,
                        ),
                        (
                            "pricelist_id.expiration_date",
                            ">=",
                            order_line.order_id.date_order,
                        ),
                        ("date_end", ">=", order_line.order_id.date_order),
                    ],
                    limit=1,
                    order="min_quantity",
                )
            )
            pricelist_id = pricelist_item_id.pricelist_id or ""
            if order_line.order_id.partner_id and pricelist_id:
                order_line.pricelist_id = pricelist_id.id
                order_line.product_uom_qty = pricelist_item_id.min_quantity
            order_line.order_id._recompute_prices()
