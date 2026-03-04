# -*- coding: utf-8 -*-
from odoo import fields, models


class ProductCategory(models.Model):
    _inherit = 'product.category'

    sequence_id = fields.Many2one(
        comodel_name='ir.sequence',
        string='Reference Sequence',
        ondelete='set null',
        help=(
            "If set, products created in this category will use this sequence "
            "to auto-generate their Internal Reference (default_code). "
            "Leave empty to fall back to the global default sequence."
        ),
    )
