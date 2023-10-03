# -*- coding: utf-8 -*-

from odoo import models, fields


class ProductDocument(models.Model):
    _name = "product.document"
    _description = "Product Documents"

    name = fields.Char(string="Document Name", required=True, copy=False)
    file = fields.Binary(
        string="Document File", attachment=True, required=True, copy=False
    )
    product_id = fields.Many2one(
        "product.template", string="Product", copy=False, ondelete="cascade"
    )
    product_variant_id = fields.Many2one(
        "product.product",
        string="Product Variant",
        copy=False,
        ondelete="cascade",
    )
