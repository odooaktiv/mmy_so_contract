# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    applied_on = fields.Selection(
        selection=[
            ("3_global", "All Products"),
            ("2_product_category", "Product Category"),
            ("1_product", "Product"),
            ("0_product_variant", "Product Variant"),
        ],
        string="Apply On",
        default="0_product_variant",
        required=True,
        help="Pricelist Item applicable on selected option",
    )

    @api.constrains("date_start", "date_end")
    def _constrains_check_start_end(self):
        for line in self:
            domain = [
                ("id", "!=", line.id),
                ("product_id", "=", line.product_id.id),
                "|",
                "&",
                ("date_start", "<=", line.date_start),
                ("date_end", ">=", line.date_start),
                "&",
                ("date_start", "<=", line.date_end),
                ("date_end", ">=", line.date_end),
            ]
            duplicate_lines = self.search(domain)
            if duplicate_lines:
                raise ValidationError(
                    "The product should have different start and end dates."
                )

    @api.onchange("product_id", "product_tmpl_id", "categ_id")
    def _onchange_rule_content(self):
        return
