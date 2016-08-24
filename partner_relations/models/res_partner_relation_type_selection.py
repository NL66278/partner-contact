# -*- coding: utf-8 -*-
# © 2014-2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
"""
For the model defined here _auto is set to False to prevent creating a
database file. All i/o operations are overridden to use a sql SELECT that
takes data from res_partner_connection_type where each type is included in the
result set twice, so it appears that the connection type and the inverse
type are separate records..

The original function _auto_init is still called because this function
normally (if _auto == True) not only creates the db tables, but it also takes
care of registering all fields in ir_model_fields. This is needed to make
the field labels translatable.
"""
from psycopg2.extensions import AsIs

from openerp import api, fields, models
from openerp.tools import drop_view_if_exists

from .res_partner_relation_type import ResPartnerRelationType


PADDING = 10


class ResPartnerRelationTypeSelection(models.Model):
    """Virtual relation types"""
    _name = 'res.partner.relation.type.selection'
    _description = 'All relation types'
    _auto = False  # Do not try to create table in _auto_init(..)
    _foreign_keys = []
    _log_access = False
    _order = 'name asc'

    type_id = fields.Many2one(
        comodel_name='res.partner.relation.type',
        string='Type',
    )
    name = fields.Char('Name')
    contact_type_this = fields.Selection(
        selection=ResPartnerRelationType._get_partner_types.im_func,
        string='Current record\'s partner type',
    )
    is_inverse = fields.Boolean(
        string="Is reverse type?",
        help="Inverse relations are from right to left partner.",
    )
    contact_type_other = fields.Selection(
        selection=ResPartnerRelationType._get_partner_types.im_func,
        string='Other record\'s partner type',
    )
    partner_category_this = fields.Many2one(
        comodel_name='res.partner.category',
        string='Current record\'s category',
    )
    partner_category_other = fields.Many2one(
        comodel_name='res.partner.category',
        string='Other record\'s category',
    )

    def _auto_init(self, cr, context=None):
        drop_view_if_exists(cr, self._table)
        cr.execute(
            """CREATE OR REPLACE VIEW %(table)s AS
            SELECT
                id * %(padding)s AS id,
                id AS type_id,
                name AS name,
                False AS is_inverse,
                contact_type_left AS contact_type_this,
                contact_type_right AS contact_type_other,
                partner_category_left AS partner_category_this,
                partner_category_right AS partner_category_other
            FROM %(underlying_table)s
            UNION SELECT
                id * %(padding)s + 1,
                id,
                name_inverse,
                True,
                contact_type_right,
                contact_type_left,
                partner_category_right,
                partner_category_left
             FROM %(underlying_table)s""",
            {
                'table': AsIs(self._table),
                'padding': PADDING,
                'underlying_table': AsIs('res_partner_relation_type'),
            })
        return super(ResPartnerRelationTypeSelection, self)._auto_init(
            cr, context=context)

    @api.multi
    def name_get(self):
        """translate name using translations from res.partner.relation.type"""
        # TODO: Can this not be done simply by taking name or inverse
        #   name of underlying model??
        ir_translation = self.env['ir.translation']
        return [
            (
                this.id,
                ir_translation._get_source(
                    'res.partner.relation.type,name_inverse'
                    if this.is_inverse
                    else 'res.partner.relation.type,name',
                    ('model',),
                    self.env.context.get('lang'),
                    this.name,
                    this.type_id.id
                )
            )
            for this in self
        ]

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        """search for translated names in res.partner.relation.type"""
        res_partner_relation_type = self.env['res.partner.relation.type']
        relations = res_partner_relation_type.search([
            ('name', operator, name)
        ])
        inverse_relations = res_partner_relation_type.search([
            ('name_inverse', operator, name),
            ('symmetric', '=', False),
        ])
        return self.search(
            [
                (
                    'id', 'in',
                    map(lambda x: x * PADDING, relations.ids) +
                    map(lambda x: x * PADDING + 1, inverse_relations.ids)
                ),
            ] + (args or []),
            limit=limit
        ).name_get()
