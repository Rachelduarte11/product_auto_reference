import logging
from odoo import api, models

_logger = logging.getLogger(__name__)

_GLOBAL_SEQUENCE_CODE = 'product.auto.ref.default'


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _get_sequence_for_company(self, sequence_code, company_id):
        IrSequence = self.env['ir.sequence']
        seq = IrSequence.search(
            [('code', '=', sequence_code), ('company_id', '=', company_id)],
            limit=1,
        )
        if not seq:
            seq = IrSequence.search(
                [('code', '=', sequence_code), ('company_id', '=', False)],
                limit=1,
            )
        return seq

    @api.model_create_multi
    def create(self, vals_list):
        company_id = self.env.company.id

        for vals in vals_list:
            if vals.get('default_code'):
                continue

            if 'company_id' in vals:
                effective_company_id = vals['company_id'] or company_id
            else:
                effective_company_id = company_id

            sequence = None

            categ_id = vals.get('categ_id')
            if categ_id:
                category = self.env['product.category'].browse(categ_id)
                if category.sequence_id:
                    seq = category.sequence_id
                    if not seq.company_id or seq.company_id.id == effective_company_id:
                        sequence = seq

            if not sequence:
                sequence = self._get_sequence_for_company(
                    _GLOBAL_SEQUENCE_CODE, effective_company_id
                )

            if sequence:
                new_ref = sequence.next_by_id()
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
