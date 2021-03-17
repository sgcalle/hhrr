# -*- coding: utf-8 -*-
{
    'name': 'Stock Request',

    'summary': """ Stock Request """,

    'description': """
        Stock Request
    """,

    'author': 'Eduwebgroup',
    'website': 'http://www.eduwebgroup.com',

    'category': 'Inventory',
    'version': '1.0',

    'depends': [
        'web',
        'portal',
        'hr',
        'stock',
        'stock_account',
    ],

    'data': [
        'security/ir.model.access.csv',
        'security/stock_request_security.xml',
        'security/stock_request_stage_security.xml',
        'views/assets.xml',
        'views/stock_picking_views.xml',
        'views/stock_request_stage_views.xml',
        'views/stock_request_views.xml',
        'views/stock_request_line_views.xml',
        'views/stock_request_portal_templates.xml',
        'views/product_template_views.xml',
        'views/hr_employee_views.xml',
        'views/product_category_views.xml',
        'data/ir_sequence_data.xml',
        'data/stock_location_route_data.xml',
        'data/stock_location_data.xml',
        'data/stock_rule_data.xml',
    ],
}