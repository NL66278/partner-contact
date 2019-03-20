# -*- coding: utf-8 -*-
# Copyright 2019 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


def migrate(cr, version):

    cr.execute(
        'UPDATE res_partner_relation_type'
        ' SET is_symmetric = false'
        ' WHERE is_symmetric IS NULL')
