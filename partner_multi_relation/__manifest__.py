# Copyright 2013-2018 Therp BV <https://therp.nl>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Partner Relations",
    "version": "11.0.2.0.0",
    "author": "Therp BV,Camptocamp,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/partner-contact",
    "complexity": "normal",
    "category": "Customer Relationship Management",
    "license": "AGPL-3",
    "depends": [
        "contacts",
        "sales_team",
        "web_domain_field",
    ],
    "demo": [
        "data/demo.xml",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/res_partner_relation_all.xml",
        "views/res_partner.xml",
        "views/res_partner_relation_type.xml",
        "views/menu.xml",
    ],
    "auto_install": False,
    "installable": True,
}
