# -*- coding: utf-8 -*-

from odoo import models, fields


class ProductProduct(models.Model):
    _inherit = "product.product"

    variant_document_ids = fields.One2many(
        "product.document", "product_variant_id", string="Documents"
    )
