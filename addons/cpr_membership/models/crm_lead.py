from odoo import models, fields


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    verify_token = fields.Char(string='Email Verify Token')
    email_verified = fields.Boolean(string='Email Verified', default=False)
