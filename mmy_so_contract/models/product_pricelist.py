# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class ProductPricelist(models.Model):
    _name = "product.pricelist"
    _inherit = ["product.pricelist", "mail.thread", "mail.activity.mixin"]

    partner_id = fields.Many2one("res.partner", string="Customer", copy=False)
    incoterms = fields.Char(string="Incoterms", copy=False)
    product_category_id = fields.Many2one(
        "product.category",
        string="Product Category",
        copy=False,
        required=True,
    )
    product_grade_level = fields.Selection(
        selection="_get_custom_selection",
        copy=False,
        required=True,
        store=True,
        string="Product Grade Level",
    )
    effective_date = fields.Datetime(
        string="Effective Date", copy=False, required=True
    )
    expiration_date = fields.Datetime(
        string="Expiration Date", copy=False, required=True
    )
    exchange_rate = fields.Char(copy=False, string="Exchange Rate")
    warranty_details = fields.Char(string="Warranty Details", copy=False)
    quality_details = fields.Char(string="Quality Details", copy=False)
    quality_check = fields.Many2one(
        "quality.check", string="Quality Check", copy=False
    )
    rebates = fields.Selection(
        selection=[
            ("Rebate ABC", "Rebate ABC"),
            ("Rebate 123", "Rebate 123"),
            ("Rebate ABC-123", "Rebate ABC-123"),
        ],
        copy=False,
        string="Rebates",
    )

    @api.onchange("product_category_id", "product_grade_level")
    def _onchange_category_grade(self):
        if self.item_ids.exists():
            self.item_ids = [(5, 0, 0)]

    def _get_custom_selection(self):
        # Fetch dynamic values based on active grade attribute
        attributes = (
            self.env["product.attribute"]
            .search([])
            .filtered(lambda attribute: attribute.is_grade)
        )
        return [
            (str(item.id), item.name.title()) for item in attributes.value_ids
        ]

    def send_documents_email(self):
        """Creates attachments and sends them in an email"""
        template_id = self.env.ref("mmy_so_contract.mail_template_pricelist")
        if not template_id:
            raise UserError(_("Mail template missing!"))

        if not self.partner_id:
            raise UserError(_("Please select a customer!"))

        attachment_ids = []
        for item in self.item_ids.filtered(
            lambda x: x.product_id or x.product_tmpl_id
        ):
            documents = (
                item.product_id.variant_document_ids
                if item.product_id and item.product_id.variant_document_ids
                else item.product_tmpl_id.document_ids
            )

            for line in documents:
                attachment_values = {
                    "name": line.name,
                    "datas": line.file,
                    "res_model": "product.pricelist",
                    "res_id": self.id,
                }
                attachment = self.env["ir.attachment"].create(
                    attachment_values
                )
                attachment_ids.append(attachment.id)

        product_grade_list = self._get_custom_selection()
        result_dict = {key: value for key, value in product_grade_list}
        product_grade_value = result_dict.get(self.product_grade_level) or ""
        email_values = {
            "email_from": self.env.user.email or False,
            "email_to": self.partner_id.email,
            "attachment_ids": [(4, att_id) for att_id in attachment_ids],
        }

        template_id.sudo().with_context(
            product_grade_value=product_grade_value
        ).send_mail(self.id, email_values=email_values, force_send=True)
        sent_mails = (
            self.env["mail.mail"]
            .sudo()
            .search(
                [
                    ("model", "=", "product.pricelist"),
                    ("res_id", "=", self.id),
                ],
                limit=1,
            )
        )
        if sent_mails:
            if sent_mails.state == "sent":
                message = _(f"Email {sent_mails.subject} sent successfully!")
                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "message": message,
                        "type": "success",
                        "sticky": False,
                    },
                }
            else:
                message = _(f"Email {sent_mails.subject} failed to send.")
                return {
                    "type": "ir.actions.client",
                    "tag": "display_notification",
                    "params": {
                        "message": message,
                        "type": "danger",
                        "sticky": False,
                    },
                }

    @api.constrains("effective_date", "expiration_date")
    def _constrains_check_dates_constrains(self):
        for line in self:
            domain = [
                ("id", "!=", line.id),
                ("effective_date", "=", line.effective_date),
                ("expiration_date", "=", line.expiration_date),
                ("partner_id", "=", line.partner_id.id),
            ]
            lines = self.search(domain)
            if lines:
                raise UserError(
                    _(
                        "The Pricelist already exists for the customer with "
                        "the same effective and expiration dates."
                    )
                )
