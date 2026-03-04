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
                new_ref = sequence.next_by_id()
                # Check for collisions. Let's keep pulling from the sequence until we find a free one.
                # To prevent infinite loops in weird scenarios, we cap it at 1000 tries.
                max_tries = 1000
                tries = 0
                while new_ref and tries < max_tries:
                    # Check if this reference already exists on a product.template or product.product
                    # Typically checking product.product is safer since default_code is usually stored there as well.
                    existing = self.env['product.product'].with_context(active_test=False).search(
                        [('default_code', '=', new_ref)], limit=1
                    )
                    if not existing:
                        break  # Found an available reference!
                    
                    # Ref exists, generate the next one
                    new_ref = sequence.next_by_id()
                    tries += 1

                if tries >= max_tries:
                    _logger.error(
                        "product_auto_reference: Exceeded %s attempts trying to find an available "
                        "reference for sequence %s. Check for infinite loops or massive data imports.",
                        max_tries, sequence.name
                    )

                vals['default_code'] = new_ref
            else:
                _logger.warning(
                    "product_auto_reference: No sequence found (neither category-specific "
                    "nor global '%s'). Product will be created without an auto-reference.",
                    _GLOBAL_SEQUENCE_CODE,
                )

        return super().create(vals_list)
