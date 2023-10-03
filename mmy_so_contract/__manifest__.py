# -*- coding: utf-8 -*-

{
    "name": "MMY Auto | SO Contract",
    "summary": """
        Manage multiple contracts on SO
    """,
    "description": """
        Manage multiple contracts and approvals on SO
    """,
    "author": "MMY Auto",
    "website": "",
    "category": "Hidden",
    "version": "16.0.0.0.0",
    "license": "LGPL-3",
    "depends": ["sale_management", "sale_temporal", "quality_control"],
    "data": [
        "data/pricelist_mail_template.xml",
        "security/ir.model.access.csv",
        "security/security.xml",
        "views/sale_order_views.xml",
        "views/product_pricelist_views.xml",
        "views/product_template_views.xml",
        "views/product_product_views.xml",
    ],
    "auto_install": False,
    "installable": True,
    "application": False,
}
