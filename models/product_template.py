# -*- coding: utf-8 -*-
import logging
from odoo import api, models

_logger = logging.getLogger(__name__)

_GLOBAL_SEQUENCE_CODE = 'product.auto.ref.default'


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _get_sequence_for_company(self, sequence_code, company_id):
        """Return the best matching ir.sequence for the given code and company.

        Priority:
          1. Sequence with this code belonging to the given company.
          2. Sequence with this code shared across all companies (company_id=False).
        """
        IrSequence = self.env['ir.sequence']
        # Company-specific sequence first
        seq = IrSequence.search(
            [('code', '=', sequence_code), ('company_id', '=', company_id)],
            limit=1,
        )
        if not seq:
            # Fall back to a shared (no-company) sequence
            seq = IrSequence.search(
                [('code', '=', sequence_code), ('company_id', '=', False)],
                limit=1,
            )
        return seq

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to auto-assign default_code when not manually provided.

        Priority order:
          1. Manual entry  → keep whatever the user typed (skip auto-generation).
          2. Category seq  → use the sequence linked to the product's category,
                             respecting the active company.
          3. Global seq    → fall back to the sequence with code
                             product.auto.ref.default, respecting the active company.
        """
        company_id = self.env.company.id

        for vals in vals_list:
            # Rule 1 – Manual entry: never overwrite an explicitly provided reference.
            if vals.get('default_code'):
                continue

            # Respetar el mismo patrón que auto_company_product:
            # - Si company_id no viene en vals → usar la empresa activa del usuario.
            # - Si viene explícitamente (incluso False para "producto compartido") → respetar.
            if 'company_id' in vals:
                effective_company_id = vals['company_id'] or company_id
            else:
                effective_company_id = company_id

            # Determine which sequence to use.
            sequence = None

            # Rule 2 – Category-specific sequence.
            categ_id = vals.get('categ_id')
            if categ_id:
                category = self.env['product.category'].browse(categ_id)
                if category.sequence_id:
                    # Honor multi-company: prefer the category sequence if it
                    # belongs to our company or is shared.
                    seq = category.sequence_id
                    if not seq.company_id or seq.company_id.id == effective_company_id:
                        sequence = seq

            # Rule 3 – Global fallback sequence (company-aware).
            if not sequence:
                sequence = self._get_sequence_for_company(
                    _GLOBAL_SEQUENCE_CODE, effective_company_id
                )

            if sequence:
                new_ref = sequence.next_by_id()
                # Collision guard – keep pulling until we find a free reference.
                # Cap at 1000 tries to avoid infinite loops on bad data.
                max_tries = 1000
                tries = 0
                while new_ref and tries < max_tries:
                    existing = self.env['product.product'].with_context(
                        active_test=False
                    ).search([('default_code', '=', new_ref)], limit=1)
                    if not existing:
                        break
                    new_ref = sequence.next_by_id()
                    tries += 1

                if tries >= max_tries:
                    _logger.error(
                        "product_auto_reference: Exceeded %s attempts finding an "
                        "available reference for sequence '%s' (company %s).",
                        max_tries, sequence.name, effective_company_id,
                    )

                vals['default_code'] = new_ref
            else:
                _logger.warning(
                    "product_auto_reference: No sequence found (neither category-specific "
                    "nor global '%s') for company %s. "
                    "Product will be created without an auto-reference.",
                    _GLOBAL_SEQUENCE_CODE, effective_company_id,
                )

        return super().create(vals_list)
