# -*- coding: utf-8 -*-

from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = "product.template"

    document_ids = fields.One2many(
        "product.document", "product_id", string="Documents"
    )
