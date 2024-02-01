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

    @api.onchange("product_template_id", "product_id")
    def _onchange_pricelist_id(self):
        for order_line in self:
            price_list = self.env["product.pricelist"].search(
                [
                    (
                        "partner_id",
                        "in",
                        [order_line.order_id.partner_id.id, False],
                    ),
                ],
            )
            if order_line.pricelist_id not in price_list:
                order_line.pricelist_id = False
            filtered_list = price_list.filtered(
                lambda rec: rec.partner_id
                and rec.effective_date
                and rec.expiration_date
                and rec.effective_date <= order_line.order_id.date_order
                and rec.expiration_date >= order_line.order_id.date_order
                and rec.item_ids.filtered(
                    lambda item: (
                        item.product_id
                        and item.product_id.id == order_line.product_id.id
                    )
                    or (
                        item.product_tmpl_id
                        and item.product_tmpl_id.id
                        == order_line.product_template_id.id
                    )
                    and item.date_start
                    and item.date_end
                    and item.date_start <= order_line.order_id.date_order
                    and item.date_end >= order_line.order_id.date_order
                )
            )
            if order_line.order_id.partner_id and filtered_list:
                order_line.pricelist_id = filtered_list[0].id
            order_line.order_id._recompute_prices()
