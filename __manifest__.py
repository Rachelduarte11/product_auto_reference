# -*- coding: utf-8 -*-
{
    'name': 'Product Auto Reference',
    'version': '18.0.1.0.0',
    'category': 'Inventory',
    'summary': 'Generates automatic internal references for products using configurable sequences.',
    'description': """
        This module automatically generates the Internal Reference (default_code)
        for products using configurable IR sequences.

        Features:
        - Manual entry always takes priority (no override if user types a value).
        - Each product category can have its own dedicated sequence.
        - A global fallback sequence (product.auto.ref.default) is used when no
          category-specific sequence is defined.
        - All sequences are fully editable from Inventory > Configuration > Product Sequences.
    """,
    'author': 'Custom Development',
    'depends': ['product', 'stock'],
    'data': [
        'data/ir_sequence_data.xml',
        'views/product_category_views.xml',
        'views/menus.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
