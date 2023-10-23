# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    is_grade = fields.Boolean(string="Is Grade Attribute")
