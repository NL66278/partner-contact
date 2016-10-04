# -*- coding: utf-8 -*-
# © 2014-2016 Therp BV <http://therp.nl>.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import api, fields, models


class ResPartnerRelationType(models.Model):
    """Show relations of certain types in own tab in partner form.

    For each relation type give the possibility to show the relations or
    the inverse relations within their own tab in the partner form. To do
    this, a field is added for each tab, showing the relations of that
    particular type.
    """
    _inherit = 'res.partner.relation.type'

    own_tab_left = fields.Boolean(
        string='Show in own tab',
        default=False,
    )
    own_tab_right = fields.Boolean(
        string='Show in own tab',
        default=False,
    )

    def _update_res_partner_fields(self):
        """On create or write, add fields needed to show tab to partner.

        If a tab is no longer defined, but a field for the tab was existing,
        delete that field.
        """
        partner_model = self.env['res.partner']

        def get_field_name(relation_type, inverse):
            """Get field name unique for relation and left or right side."""
            return (
                'relation_ids_own_tab_%s_%s' % (
                    relation_type.id,
                    'left' if not inverse else 'right',
                )
            )

        def add_field(relation_type, inverse):
            """Add field to show relations in own tab."""
            field = fields.One2many(
                comodel_name='res.partner.relation',
                inverse_name='%s_partner_id' % (
                    'left' if not inverse else 'right'),
                string=relation_type[
                    'name' if not inverse else 'name_inverse'],
                domain=[
                    ('type_id', '=', relation_type.id),
                    '|',
                    ('active', '=', True),
                    ('active', '=', False),
                ]
            )
            field_name = get_field_name(relation_type, inverse)
            partner_model._add_field([field_name], field)

        def del_field(relation_type, inverse):
            """Delete field for tab."""
            field_name = get_field_name(relation_type, inverse)
            if field_name in partner_model._fields:
                partner_model._pop_field([field_name])

        sudo_self = self.sudo().browse(self.ids)
        for rec in sudo_self:
            if rec.own_tab_left:
                add_field(rec, False)
            else:
                del_field(rec, False)
            if rec.own_tab_right:
                add_field(rec, True)
            else:
                del_field(rec, True)

    def _register_hook(self, cr):
        self._update_res_partner_fields()

    @api.model()
    def create(self, vals):
        result = super(ResPartnerRelationType, self).create(vals)
        if vals.get('own_tab_left') or vals.get('own_tab_right'):
            self._update_res_partner_fields()
        return result

    @api.multi()
    def write(self, vals):
        result = super(ResPartnerRelationType, self).write(vals)
        if 'own_tab_left' in vals or 'own_tab_right' in vals:
            self._update_res_partner_fields()
        return result
