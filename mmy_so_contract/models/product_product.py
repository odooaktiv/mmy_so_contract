# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductProduct(models.Model):
    _inherit = "product.product"

    variant_document_ids = fields.One2many(
        "mmy.product.document", "product_variant_id", string="Documents"
    )

    @api.model
    def _search(
        self,
        args,
        offset=0,
        limit=None,
        order=None,
        access_rights_uid=None,
    ):
        if self._context.get("categ_id") and self._context.get("grade_id"):
            subcategories_ids = self.env["product.category"].search(
                [("id", "child_of", self._context.get("categ_id"))]
            )
            args += (
                [("categ_id", "in", subcategories_ids.ids)]
                if subcategories_ids
                else []
            )
            args += [
                (
                    "product_template_attribute_value_ids."
                    "product_attribute_value_id",
                    "=",
                    int(self._context.get("grade_id")),
                )
            ]
        return super(ProductProduct, self)._search(
            args, offset, limit, order, access_rights_uid
        )
