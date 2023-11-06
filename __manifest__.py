# -*- coding: utf-8 -*-
{
    'name': "AMELIORATION CNAM",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Index Consulting Madagascar",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'index_custom_cnam', 'edu_management'],

    # always loaded
    'data': [
        'views/assets.xml',
        'security/ir.model.access.csv',
        'views/inscription.xml',
        'data/email_template.xml',
        'data/cron.xml',
        'data/groups.xml',
        'views/pointage_xlsx.xml',
        'views/engagement.xml',
        'views/note_list.xml',
        "views/convocation.xml",
        "views/convocation_template.xml",
    ],
}
