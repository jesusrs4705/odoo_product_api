{
    'name': 'Custom Product API',
    'version': '1.0',
    'summary': 'API para crear y actualizar productos',
    'description': """
        Este módulo proporciona un endpoint para crear o actualizar productos en Odoo.
        Se puede acceder mediante una petición POST con datos JSON.
    """,
    'category': 'Inventory/Sales',
    'author': 'Jesus Rodriguez',
    'depends': ['base', 'product', 'stock', 'sale_management'],
    'data': [
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}