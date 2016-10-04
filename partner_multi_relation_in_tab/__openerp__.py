# -*- coding: utf-8 -*-
# © 2014-2016 Therp BV <http://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Show partner relations in own tab',
    'version': '8.0.1.0.0',
    'author': 'Therp BV,Odoo Community Association (OCA)',
    'license': 'AGPL-3',
    'complexity': 'normal',
    'category': 'Customer Relationship Management',
    'depends': [
        'partner_relations',
    ],
    'data': [
        'view/res_partner_relation_type.xml',
    ],
    'auto_install': False,
    'installable': True,
    'application': False,
}
