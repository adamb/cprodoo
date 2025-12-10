import json
import logging
from odoo import http, fields
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
            product_name = session.get('metadata', {}).get('product_name', 'Day Pass')
            
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
                    
                    # Create portal user and send invitation
                    self._create_portal_user(partner)
                else:
                    _logger.info("Found existing contact: %s", partner.name)
                
                # Create invoice
                if amount > 0:
                    self._create_invoice(partner, amount, product_name, session.get('id'))
        
        elif event['type'] == 'invoice.paid':
            # Handle recurring subscription payment
            invoice_data = event['data']['object']
            customer_email = invoice_data.get('customer_email')
            amount = invoice_data.get('amount_paid', 0) / 100
            subscription_id = invoice_data.get('subscription')
            
            _logger.info("Recurring payment: %s - $%s", customer_email, amount)
            
            if customer_email and amount > 0:
                Partner = request.env['res.partner'].sudo()
                partner = Partner.search([('email', '=', customer_email)], limit=1)
                
                if partner:
                    # Create invoice for recurring payment
                    product_name = "Membership Renewal"
                    self._create_invoice(partner, amount, product_name, f"sub_{subscription_id}")
                    _logger.info("Created recurring invoice for %s", partner.name)
                else:
                    _logger.warning("No contact found for recurring payment: %s", customer_email)
        
        return {'status': 'ok'}

    
    def _create_portal_user(self, partner):
        """Create a portal user and send invitation email"""
        try:
            User = request.env['res.users'].sudo()
            existing_user = User.search([('login', '=', partner.email)], limit=1)
            
            if existing_user:
                _logger.info("User already exists for %s", partner.email)
                return
            
            user = User.create({
                'login': partner.email,
                'partner_id': partner.id,
                'groups_id': [(6, 0, [request.env.ref('base.group_portal').id])],
            })
            
            user.action_reset_password()
            
            _logger.info("Created portal user and sent invitation to %s", partner.email)
            
        except Exception as e:
            _logger.error("Failed to create portal user: %s", str(e))
    
    def _create_invoice(self, partner, amount, product_name, stripe_session_id):
        """Create and post an invoice for the Stripe payment"""
        try:
            Invoice = request.env['account.move'].sudo()
            
            invoice = Invoice.create({
                'move_type': 'out_invoice',
                'partner_id': partner.id,
                'invoice_date': fields.Date.today(),
                'ref': f'Stripe: {stripe_session_id}',
                'invoice_line_ids': [(0, 0, {
                    'name': product_name,
                    'quantity': 1,
                    'price_unit': amount,
                })],
            })
            
            invoice.action_post()
            self._register_payment(invoice, amount)
            
            _logger.info("Created invoice %s for %s", invoice.name, partner.name)
            
        except Exception as e:
            _logger.error("Failed to create invoice: %s", str(e))
    
    def _register_payment(self, invoice, amount):
        """Mark the invoice as paid"""
        try:
            Payment = request.env['account.payment.register'].sudo()
            
            payment_wizard = Payment.with_context(
                active_model='account.move',
                active_ids=invoice.ids
            ).create({
                'amount': amount,
                'payment_date': fields.Date.today(),
            })
            payment_wizard.action_create_payments()
            
            _logger.info("Payment registered for invoice %s", invoice.name)
            
        except Exception as e:
            _logger.error("Failed to register payment: %s", str(e))

    
