from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    membership_type = fields.Selection([
        ('hot_desk', 'Hot Desk'),
    ], string='Membership Type')
    membership_start = fields.Date(string='Membership Start Date')
    access_key_id = fields.Char(string='Salto Access Key ID')
