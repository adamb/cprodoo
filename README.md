# CPR Odoo - Code Puerto Rico Coworking Portal

A self-hosted Odoo-based membership management system for the CPR coworking space.

## Features

- Member management with custom fields (membership type, start date, access key)
- Hot Desk membership ($250/month, annual contract, includes $150 meeting room credits)
- Public website with membership application form
- Google OAuth login (Sign in with Google)
- OCA membership extensions for enhanced membership management
- Salto access key tracking (integration stubbed)
- Stripe payment integration with automatic invoicing
- Event interest signup form with email verification (creates CRM leads)
- Workshop pages with dedicated URLs and registration forms
- UTM marketing attribution tracking on all signups (source, medium, campaign)
- Blog with event recaps and community content
- Website pages managed via Odoo MCP server

## Requirements

- Docker
- Docker Compose
- Git (with submodule support)

## Setup

1. Clone this repository with submodules:
git clone --recurse-submodules cd cprodoo

Copied!
2. Copy `.env.example` to `.env` and fill in your credentials

3. Build and start the containers:
docker-compose build docker-compose up -d

4. Access Odoo at http://localhost:8069

5. Create a new database when prompted

6. Enable Developer Mode (Settings → Activate developer mode)

7. Install modules:
- Go to Apps → Update Apps List
- Search for and activate: "CPR Membership", "Members", "Membership Extension", "Website", "auth_oidc", "CRM", "Contact Form"

## Backup and Restore

Backup your instance:
./scripts/backup.sh

Copied!
Restore from backup:
./scripts/restore.sh backup_YYYYMMDD_HHMMSS.tar.gz

Copied!
These scripts work on both Mac and Linux (Debian).

## Project Structure

- `addons/cpr_membership/` - Custom membership module (members, events, workshops, blog overrides)
- `addons/vertical-association/` - OCA membership modules (submodule)
- `addons/server-auth/` - OCA authentication modules (submodule)
- `scripts/` - Backup and restore scripts
- `Dockerfile` - Custom Odoo image with additional dependencies
- `docker-compose.yml` - Docker services configuration
- `.env` - Environment variables (not in git)

## Deployment

Production instance runs at https://code.pr via Cloudflare Tunnel on a Linode server.

To deploy code changes:
```bash
git push origin main
ssh adam@172.235.135.83 "cd ~/code/cprodoo && git pull origin main"
# If models changed, upgrade the module:
ssh adam@172.235.135.83 "cd ~/code/cprodoo && docker-compose run --rm odoo odoo -d cpr -u cpr_membership --stop-after-init"
# Always restart after deploying:
ssh adam@172.235.135.83 "cd ~/code/cprodoo && docker-compose restart odoo"
```


## Development Workflow (Claude Code + Odoo MCP)

This project is developed using [Claude Code](https://claude.ai/code) with an [Odoo MCP server](https://github.com/ivnvxd/mcp-server-odoo) that gives Claude direct read/write access to the live Odoo instance.

This means Claude can do two types of work in a single conversation:

**Website content changes (no deploy needed):**
- Edit page content, add events, update team bios, restructure sections
- Upload images as Odoo attachments
- Create/update any Odoo database records (contacts, tags, CRM leads, etc.)

These changes go directly to the database via the MCP server and are live immediately.

**Code changes (deploy needed):**
- New controllers, models, or views in `addons/cpr_membership/`
- Changes to `__manifest__.py` dependencies
- Any Python or XML file changes

These require a git push + pull on the server + module upgrade + restart (see Deployment section).

### MCP Server Setup

The Odoo MCP server is configured per-project in Claude Code:

```bash
claude mcp add odoo \
  --env ODOO_URL=https://code.pr \
  --env ODOO_USER=adam@code.pr \
  --env ODOO_API_KEY=<your-api-key> \
  --env ODOO_DB=cpr \
  --env ODOO_YOLO=true \
  -- uvx mcp-server-odoo
```

To generate an API key: Odoo → user avatar → My Profile → Account Security → API Keys → New API Key.

`ODOO_YOLO=true` enables read/write access via standard XML-RPC without needing the `mcp_server` Odoo module installed. Use `ODOO_YOLO=read` for read-only access.

## Workshops

Workshop pages live at `/workshops/<slug>` with a listing at `/workshops`. Each workshop has its own dedicated page with a registration form that creates CRM leads.

### Adding a new workshop

1. Create an `ir.ui.view` with the workshop page content (use the Linux workshop view id 2030 as a template)
2. Create a `website.page` record pointing to that view with the desired URL
3. Add the event key to `VALID_EVENTS` in `addons/cpr_membership/controllers/event_interest.py`
4. Add a card to the `/workshops` listing page (view id 2031)
5. Optionally add a summary card to `/upcoming-events` (view id 1827) linking to the workshop page
6. Deploy the code change and restart Odoo

### UTM marketing attribution

All registration forms support UTM tracking via URL parameters. Share links like:

```
https://code.pr/workshops/linux-workshop?utm_source=instagram&utm_medium=social&utm_campaign=linux-may2026
```

The `utm_source`, `utm_medium`, and `utm_campaign` values are captured by JavaScript on the page, submitted as hidden form fields, and stored on the CRM lead using Odoo's built-in UTM models. You can filter leads by source/medium/campaign in the CRM to evaluate which marketing channels are working.

### Notification emails

When someone registers, an email is sent to `leads@code.pr`. Workshop-specific recipients can be added in `event_interest.py` (e.g., `owen@reala.io` receives Linux workshop signups).

## Blog

The blog is powered by Odoo's `website_blog` module. Blog listing is at `/blog`. Posts are created as `blog.post` records via the Odoo UI or MCP.

The blog cover banner on the listing page is hidden by a custom view override in `addons/cpr_membership/views/blog_views.xml`.

## Email Delivery (Odoo + Postfix + ImprovMX)

This project does not send email directly from Odoo to ImprovMX.

Instead, we use a Postfix sidecar container as a local MTA to avoid blocking, timeouts, and relay issues inside Odoo.

Why this setup
	•	Odoo sends emails synchronously in some code paths (login, password reset, new device alerts).
	•	If the SMTP provider is slow or disconnects, Odoo requests block or fail.
	•	ImprovMX enforces strict envelope sender rules (must match the authenticated domain).
	•	Odoo is inconsistent about envelope senders (bounce@domain, <>, etc.), especially across versions.

Using Postfix as a relay solves all of this cleanly.

Architecture

Odoo  →  Postfix (plain SMTP, port 25)  →  ImprovMX (TLS + auth)

	•	Odoo talks to Postfix over the internal Docker network
	•	Postfix handles TLS, auth, retries, and relay rules
	•	ImprovMX only ever sees approved senders (info@code.pr)

Docker Compose

A Postfix service is defined in docker-compose.yml:

postfix:
  image: boky/postfix
  restart: unless-stopped
  environment:
    - RELAYHOST=[smtp.improvmx.com]:587
    - RELAYHOST_USERNAME=${IMPROVMX_SMTP_USER}
    - RELAYHOST_PASSWORD=${IMPROVMX_SMTP_PASS}
    - SMTP_USE_TLS=yes
    - ALLOWED_SENDER_DOMAINS=code.pr
    - POSTFIX_myhostname=mailrelay.code.pr
    - POSTFIX_inet_protocols=ipv4
  volumes:
    - postfix_spool:/var/spool/postfix

ImprovMX credentials are stored in .env:

IMPROVMX_SMTP_USER=info@code.pr
IMPROVMX_SMTP_PASS=...

Odoo configuration

In Odoo → Settings → Technical → Emails → Outgoing Mail Servers:
	•	SMTP Server: postfix
	•	Port: 25
	•	Encryption: None
	•	Username / Password: empty

Odoo must not talk directly to ImprovMX.

In Settings → General Settings → Emails:
	•	Default From Alias: info
	•	Bounce Alias: bounce
	•	Catchall Alias: catchall

This ensures the envelope sender is always info@code.pr.

Debugging

Watch Postfix live:

docker-compose logs -f postfix

You should see:

from=<info@code.pr>
status=sent (250 2.0.0 Email queued for delivery)

If emails fail:
	•	Check Odoo’s email queue (Settings → Technical → Emails)
	•	Check Postfix logs
	•	Clear old queues if needed:

docker exec -it cprodoo_postfix_1 postsuper -d ALL

Notes
	•	This setup intentionally avoids AWS SES.
	•	Postfix is used only as a relay, not a public mail server.
	•	No ports are exposed to the host.


## License

TBD