import json
import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class StripeWebhookController(http.Controller):

    @http.route('/cpr_membership/stripe/webhook', type='json', auth='public', methods=['POST'], csrf=False)
    def stripe_webhook(self):
        payload = request.httprequest.data
        event = json.loads(payload)
        
        _logger.info("CPR Stripe webhook received: %s", event.get('type'))
        
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            customer_email = session.get('customer_details', {}).get('email')
            customer_name = session.get('customer_details', {}).get('name')
            amount = session.get('amount_total', 0) / 100
            
            _logger.info("Checkout completed: %s - %s - $%s", customer_name, customer_email, amount)
            
            if customer_email:
                Partner = request.env['res.partner'].sudo()
                partner = Partner.search([('email', '=', customer_email)], limit=1)
                
                if not partner:
                    partner = Partner.create({
                        'name': customer_name or customer_email,
                        'email': customer_email,
                    })
                    _logger.info("Created new contact: %s", partner.name)
                else:
                    _logger.info("Found existing contact: %s", partner.name)
        
        return {'status': 'ok'}
