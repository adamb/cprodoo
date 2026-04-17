{
    'name': 'CPR Membership',
    'version': '1.0.0',
    'depends': ['contacts', 'crm', 'website', 'website_blog'],
    'author': 'Code Puerto Rico',
    'category': 'Sales',
    'description': """
        Coworking membership management for CPR
    """,
    'data': [
        'views/member_views.xml',
        'views/crm_lead_views.xml',
        'views/blog_views.xml',
    ],
    'installable': True,
    'application': False,
}
