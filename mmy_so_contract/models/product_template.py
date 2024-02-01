# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = "product.template"

    document_ids = fields.One2many(
        "mmy.product.document", "product_id", string="Documents"
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
                    "attribute_line_ids.value_ids",
                    "in",
                    [self._context.get("grade_id")],
                )
            ]
        return super(ProductTemplate, self)._search(
            args, offset, limit, order, access_rights_uid
        )
