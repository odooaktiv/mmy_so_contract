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
    date_end = fields.Datetime(
        string="End Date",
        help="Ending datetime for the pricelist item validation\n"
        "The displayed value depends on the timezone set in your preferences.",
    )

    @api.model_create_multi
    def create(self, vals_list):
        records = super(ProductPricelistItem, self).create(vals_list)
        [
            record.write({"date_end": record.pricelist_id.expiration_date})
            for record in records
            if not record.date_end
        ]
        return records

    @api.constrains("date_start", "date_end")
    def _constrains_check_start_end(self):
        for line in self:
            if line.date_start or line.date_start:
                domain = [
                    ("id", "!=", line.id),
                    ("pricelist_id", "=", line.pricelist_id.id),
                    ("product_id", "=", line.product_id.id),
                    "|",
                    "&",
                    ("date_start", "<=", line.date_start),
                    ("date_end", ">=", line.date_start),
                    "&",
                    ("date_start", "<=", line.date_end),
                    ("date_end", ">=", line.date_end),
                ]
            else:
                domain = [
                    ("id", "!=", line.id),
                    ("pricelist_id", "=", line.pricelist_id.id),
                    ("product_id", "=", line.product_id.id),
                    ("date_start", "=", False),
                    ("date_end", "=", False),
                ]
            duplicate_lines = self.search(domain)
            if duplicate_lines:
                raise ValidationError(
                    _(
                        "Repeating Products should have different start and "
                        "end date."
                    )
                )

    @api.constrains("min_quantity", "fixed_price")
    def _constrains_check_min_quantity(self):
        for line in self:
            domain = [
                ("pricelist_id", "=", line.pricelist_id.id),
                ("product_id", "=", line.product_id.id),
                "|",
                ("min_quantity", "<=", 0.0),
                ("fixed_price", "<=", 0.0),
                ("compute_price", "=", "fixed"),
            ]
            lines = self.search(domain)
            if lines:
                raise ValidationError(
                    _(
                        "The product should have Fixed Price and Min Quantity"
                        " greater than 0."
                    )
                )

    @api.onchange("product_id", "product_tmpl_id", "categ_id")
    def _onchange_rule_content(self):
        if (
            not self.pricelist_id.product_category_id
            or not self.pricelist_id.product_grade_level
        ):
            raise ValidationError(
                _(
                    "Pricelist should have 'Product Category'"
                    " and 'Product Grade Level'."
                )
            )
        return
