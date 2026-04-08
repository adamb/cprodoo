# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CPR Odoo is a self-hosted Odoo 18.0 membership management system for the Code Puerto Rico coworking space (https://code.pr). It handles member accounts, Stripe payments, Google OAuth login, and invoicing.

## Architecture

Three Docker services defined in `docker-compose.yml`:
- **postgres:15** - Database
- **postfix** (boky/postfix) - Local MTA relay to ImprovMX (decouples Odoo from slow SMTP)
- **odoo:18.0** (custom Dockerfile adding python3-jose) - Web app on port 8069, reverse-proxied via Cloudflare Tunnel

Odoo talks to Postfix over internal Docker network (port 25, no auth). Postfix relays to ImprovMX with TLS. All envelope senders must be `info@code.pr`.

## Custom Code

All custom code lives in `addons/cpr_membership/`:
- `models/member.py` - Extends `res.partner` with `membership_type`, `membership_start`, `access_key_id`
- `models/crm_lead.py` - Extends `crm.lead` with `verify_token`, `email_verified` for event interest signups
- `controllers/stripe_webhook.py` - Handles Stripe events at `/cpr_membership/stripe/webhook`
  - `checkout.session.completed` → creates contact, portal user, invoice, registers payment
  - `invoice.paid` → handles recurring subscription renewals
- `controllers/event_interest.py` - Event interest signup form with email verification
  - `POST /cpr_membership/event_interest` → creates CRM lead tagged "Unverified", sends verification email
  - `GET /cpr_membership/verify_email?token=...` → marks lead as "Verified"
- `views/member_views.xml` - Adds Membership tab to contact form
- `__manifest__.py` - Depends on `contacts`, `crm`, `website` modules

Two OCA Git submodules in `addons/`:
- `vertical-association/` - Membership extensions (prorating, variable periods)
- `server-auth/` - Authentication modules (OIDC for Google OAuth)

## Common Commands

```bash
# Build and run
docker-compose build
docker-compose up -d
docker-compose down

# View logs
docker-compose logs -f odoo
docker-compose logs -f postfix

# Backup / Restore
./scripts/backup.sh                              # Creates backup_YYYYMMDD_HHMMSS.tar.gz
./scripts/restore.sh backup_YYYYMMDD_HHMMSS.tar.gz

# Odoo shell access
docker exec -it cprodoo_odoo_1 odoo shell

# Test Stripe webhooks locally
stripe listen --forward-to localhost:8069/cpr_membership/stripe/webhook

# Deploy code changes to production
git push origin main
ssh adam@172.235.135.83 "cd ~/code/cprodoo && git pull origin main"
# If models changed, upgrade the module:
ssh adam@172.235.135.83 "cd ~/code/cprodoo && docker-compose run --rm odoo odoo -d cpr -u cpr_membership --stop-after-init"
# Always restart after deploying:
ssh adam@172.235.135.83 "cd ~/code/cprodoo && docker-compose restart odoo"
```

## Environment

Credentials in `.env` (see `.env.example`). Key vars: `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `ODOO_MASTER_PASSWORD`, `IMPROVMX_SMTP_USER`, `IMPROVMX_SMTP_PASS`.

## Development Notes

- No automated test suite. Testing is manual via Odoo UI and Stripe CLI.
- Clone with `--recurse-submodules` to get OCA modules.
- After starting, create DB via Odoo wizard at localhost:8069, then install modules via Apps menu.
- Odoo manages schema automatically from model definitions; no explicit migrations.
- Odoo conventions: models use `_inherit` to extend existing models, views use XML inheritance, controllers are `http.Controller` subclasses with `@http.route` decorators.
