import logging
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
        for label in event_labels:
            tag = CrmTag.search([('name', '=', label)], limit=1)
            if not tag:
                tag = CrmTag.create({'name': label})
            crm_tag_ids.append(tag.id)

        # Create CRM lead
        Lead = request.env['crm.lead'].sudo()
        lead = Lead.create({
            'name': ', '.join(event_labels),
            'contact_name': name,
            'email_from': email,
            'description': f"Event interest signup from website.\nEvents: {', '.join(event_labels)}",
            'tag_ids': [(6, 0, crm_tag_ids)],
            'type': 'lead',
        })
        _logger.info("Created event interest lead %s for %s (%s)", lead.id, name, email)

        # Send confirmation email
        event_list = ''.join(f'<li>{label}</li>' for label in event_labels)
        try:
            Mail = request.env['mail.mail'].sudo()
            Mail.create({
                'subject': 'Code Puerto Rico — You\'re on the list!',
                'email_from': 'info@code.pr',
                'email_to': email,
                'body_html': f'''<div style="font-family: sans-serif;">
<p>Hi {name},</p>
<p>Thanks for your interest! We'll notify you when these events are scheduled:</p>
<ul>{event_list}</ul>
<p>In the meantime, check out our <a href="https://code.pr/upcoming-events">upcoming events</a> for things happening soon.</p>
<p>See you there!<br/>The Code Puerto Rico Team</p>
</div>''',
            }).send()
        except Exception as e:
            _logger.error("Failed to send confirmation email to %s: %s", email, e)

        return request.redirect('/upcoming-events-thanks')

    @http.route('/upcoming-events-thanks', type='http', auth='public',
                website=True)
    def event_interest_thanks(self, **kwargs):
        return request.render('website.upcoming-events-thanks', {})
