# -*- coding: utf-8 -*-
# © 2013-2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import _, api, exceptions, fields, models
from openerp.osv.expression import FALSE_LEAF


PADDING = 10


class ResPartnerRelationWizard(models.TransientModel):
    """Wizard to easily add or change a new relation between two partners."""
    _name = 'res.partner.relation.wizard'
    _description = 'Partner relation wizard'
    _order = 'active desc, date_start desc, date_end desc'

    type_selection_id = fields.Many2one(
        comodel_name='res.partner.relation.type.selection',
        compute='_compute_fields',
        inverse=lambda *args: None,
        string='Type',
    )
    this_partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Source Partner',
        required=True,
        auto_join=True,
        ondelete='cascade',
    )
    other_partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Destination Partner',
        required=True,
        auto_join=True,
        ondelete='cascade',
    )
    date_start = fields.Date('Starting date')
    date_end = fields.Date('Ending date')
    active = fields.Boolean('Active', default=True)

    @api.multi
    def _compute_fields(self):
        for this in self:
            on_right_partner = this._on_right_partner()
            this.type_selection_id = self\
                .env['res.partner.relation.type.selection']\
                .browse(this.type_id.id * PADDING +
                        (on_right_partner and 1 or 0))

    @api.onchange('type_selection_id')
    def _onchange_type_selection_id(self):
        """Set domain on left and right partner on change of relation type"""
        result = {
            'domain': {
                'left_partner_id': [FALSE_LEAF],
                'right_partner_id': [FALSE_LEAF],
            },
        }
        # TODO: totally rewrite. For the moment disable:
        return result
        # END TODO 
        if not self.type_selection_id:
            return result
        type_id, is_reverse = self.type_selection_id\
            .get_type_from_selection_id()
        self.type_id = self.env['res.partner.relation.type'].browse(type_id)
        partner_domain = []
        check_contact_type = self.type_id.contact_type_right
        check_partner_category = self.type_id.partner_category_right
        if is_reverse:
            check_contact_type = self.type_id.contact_type_left
            check_partner_category = self.type_id.partner_category_left
        if check_contact_type == 'c':
            partner_domain.append(('is_company', '=', True))
        if check_contact_type == 'p':
            partner_domain.append(('is_company', '=', False))
        if check_partner_category:
            partner_domain.append(
                ('category_id', 'child_of', check_partner_category.ids))
        result['domain']['left_partner_id'] = partner_domain
        return result

    @api.multi
    def _on_right_partner(self):
        """Determine wether functions are called in a situation where the
        active partner is the right partner. Default False!
        """
        return set(self.mapped('right_partner_id').ids) &\
            set(self.env.context.get('active_ids', []))
