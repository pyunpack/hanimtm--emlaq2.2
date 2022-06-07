 # -*- coding: utf-8 -*-

{
    'name': 'Alemlaq Sale Margin Customisation',
    'author': 'AMCL',
    'category': 'Sales',
    'summary': 'Alemlaq Sale Margin Customisation',
    'description': '''
        Alemlaq Sale Margin Customisation
                    ''',
    'version': '15.0.1',
    'depends': ['sale_management','sales_team'],
    'application': True,
    'data': [
            'wizard/price_change_request_view.xml',
            'views/globalmargin.xml',
            'views/product.xml',
            'views/sale_price_approval.xml',
            'views/price_approval_view.xml',
            'views/sale_order_views.xml',
            'security/ir.model.access.csv',
            'data/data.xml',

    ],
    'license': 'LGPL-3',
    'auto_install': False,
    'installable': True,

}
