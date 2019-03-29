# -*- coding: utf-8 -*-
{
    'name': "xmarts_zonas",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Modulo de zonas para direcciones de entrega en clientes
    """,

    'author': "Xmats",
    'website': "www.xmarts.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','contacts'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        #'reports/cfdi_report.xml',
        'reports/invoice_report.xml',
        'reports/layout.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}