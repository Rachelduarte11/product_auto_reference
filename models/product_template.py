# -*- coding: utf-8 -*-
import logging
from odoo import api, models

_logger = logging.getLogger(__name__)

_GLOBAL_SEQUENCE_CODE = 'product.auto.ref.default'


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to auto-assign default_code when not manually provided.

        Priority order:
          1. Manual entry  → keep whatever the user typed (skip auto-generation).
          2. Category seq  → use the sequence linked to the product's category.
          3. Global seq    → fall back to the sequence with code product.auto.ref.default.
        """
        IrSequence = self.env['ir.sequence']

        for vals in vals_list:
            # Rule 1 – Manual entry: never overwrite an explicitly provided reference.
            if vals.get('default_code'):
                continue

            # Determine which sequence to use.
            sequence = None

            # Rule 2 – Category-specific sequence.
            categ_id = vals.get('categ_id')
            if categ_id:
                category = self.env['product.category'].browse(categ_id)
                if category.sequence_id:
                    sequence = category.sequence_id

            # Rule 3 – Global fallback sequence.
            if not sequence:
                sequence = IrSequence.search(
                    [('code', '=', _GLOBAL_SEQUENCE_CODE)], limit=1
                )

            if sequence:
                vals['default_code'] = sequence.next_by_id()
            else:
                _logger.warning(
                    "product_auto_reference: No sequence found (neither category-specific "
                    "nor global '%s'). Product will be created without an auto-reference.",
                    _GLOBAL_SEQUENCE_CODE,
                )

        return super().create(vals_list)
