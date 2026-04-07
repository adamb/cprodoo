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

        return request.redirect('/upcoming-events?success=1')
