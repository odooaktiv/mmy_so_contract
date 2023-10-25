# -*- coding: utf-8 -*-

from odoo import models, fields


class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    is_grade = fields.Boolean(string="Is Grade Attribute")
