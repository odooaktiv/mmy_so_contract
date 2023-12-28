# -*- coding: utf-8 -*-

from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    pricelist_id = fields.Many2one(
        string="Contract", comodel_name="product.pricelist"
    )

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
