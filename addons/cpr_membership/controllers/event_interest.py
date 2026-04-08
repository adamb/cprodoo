import logging
import secrets
from markupsafe import Markup
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

VALID_EVENTS = {
    'demo_nights': 'Interest: Demo Nights & Lightning Talks',
    'ai_coding': 'Interest: AI Coding Tools',
    'pitch_prototype': 'Interest: Pitch and Prototype',
    'cloudflare': 'Interest: Cloudflare Meetup',
    'home_assistant': 'Interest: Home Assistant Meetup',
}


class EventInterestController(http.Controller):

    @http.route('/cpr_membership/event_interest', type='http', auth='public',
                methods=['POST'], website=True, csrf=True)
    def event_interest(self, **kwargs):
        name = kwargs.get('name', '').strip()
        email = kwargs.get('email', '').strip()
        event_keys = kwargs.getlist('events') if hasattr(kwargs, 'getlist') else []

        # Handle checkbox values from form post
        if not event_keys:
            event_keys = [k for k in kwargs if k in VALID_EVENTS and kwargs[k]]

        if not name or not email:
            return request.redirect('/upcoming-events?error=missing')

        event_labels = [VALID_EVENTS[k] for k in event_keys if k in VALID_EVENTS]
        if not event_labels:
            return request.redirect('/upcoming-events?error=no_events')

        # Find or create CRM tags
        CrmTag = request.env['crm.tag'].sudo()
        crm_tag_ids = []
        unverified_tag = CrmTag.search([('name', '=', 'Unverified')], limit=1)
        if not unverified_tag:
            unverified_tag = CrmTag.create({'name': 'Unverified'})
        for label in event_labels:
            tag = CrmTag.search([('name', '=', label)], limit=1)
            if not tag:
                tag = CrmTag.create({'name': label})
            crm_tag_ids.append(tag.id)
        crm_tag_ids.append(unverified_tag.id)

        # Generate verification token
        token = secrets.token_urlsafe(32)

        # Create CRM lead
        Lead = request.env['crm.lead'].sudo()
        lead = Lead.create({
            'name': ', '.join(event_labels),
            'contact_name': name,
            'email_from': email,
            'description': f"Event interest signup from website.\nEvents: {', '.join(event_labels)}",
            'tag_ids': [(6, 0, crm_tag_ids)],
            'type': 'lead',
            'verify_token': token,
            'email_verified': False,
        })
        _logger.info("Created event interest lead %s for %s (%s)", lead.id, name, email)

        # Send verification email
        verify_url = f"https://code.pr/cpr_membership/verify_email?token={token}"
        event_list = ''.join(f'<li>{label}</li>' for label in event_labels)
        try:
            Mail = request.env['mail.mail'].sudo()
            Mail.create({
                'subject': 'Code Puerto Rico — Verify your email',
                'email_from': 'info@code.pr',
                'email_to': email,
                'body_html': f'''<div style="font-family: sans-serif;">
<p>Hi {name},</p>
<p>Thanks for your interest! Please verify your email to confirm you'd like to be notified about:</p>
<ul>{event_list}</ul>
<p style="margin: 24px 0;"><a href="{verify_url}" style="background-color: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; font-size: 16px;">Verify My Email</a></p>
<p>Or copy this link: {verify_url}</p>
<p>See you there!<br/>The Code Puerto Rico Team</p>
</div>''',
            }).send()
        except Exception as e:
            _logger.error("Failed to send verification email to %s: %s", email, e)

        return request.redirect('/upcoming-events-thanks')

    @http.route('/cpr_membership/verify_email', type='http', auth='public',
                website=True)
    def verify_email(self, token=None, **kwargs):
        if not token:
            return request.redirect('/upcoming-events')

        Lead = request.env['crm.lead'].sudo()
        lead = Lead.search([('verify_token', '=', token)], limit=1)

        if not lead:
            return request.render('website.upcoming-events-verify', {
                'verified': False,
                'message': 'Invalid or expired verification link.',
            })

        # Mark as verified
        lead.email_verified = True
        lead.verify_token = False

        # Remove "Unverified" tag, add "Verified"
        CrmTag = request.env['crm.tag'].sudo()
        unverified_tag = CrmTag.search([('name', '=', 'Unverified')], limit=1)
        verified_tag = CrmTag.search([('name', '=', 'Verified')], limit=1)
        if not verified_tag:
            verified_tag = CrmTag.create({'name': 'Verified'})

        tags_to_remove = [(3, unverified_tag.id)] if unverified_tag else []
        tags_to_add = [(4, verified_tag.id)]
        lead.write({'tag_ids': tags_to_remove + tags_to_add})

        _logger.info("Email verified for lead %s (%s)", lead.id, lead.email_from)

        return request.render('website.upcoming-events-verify', {
            'verified': True,
            'message': '',
        })

    @http.route('/upcoming-events-thanks', type='http', auth='public',
                website=True)
    def event_interest_thanks(self, **kwargs):
        return request.render('website.upcoming-events-thanks', {})
