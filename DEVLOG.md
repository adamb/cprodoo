2025-12-09 14:34:01

Get it running on my mac again.

Where is the latest?  Did i move it to debs?

adam@debian12:~/code/cprodoo$ ls -lrt
total 108768
-rw-r--r-- 1 adam adam 27704679 Nov 29 19:46 backup_20251129_194610.tar.gz
-rw-r--r-- 1 adam adam 27716900 Dec  1 13:24 backup_20251201_132418.tar.gz
-rw-r--r-- 1 adam adam 27979075 Dec  1 15:33 backup_20251201_163303.tar.gz
drwxr-xr-x 2 adam adam     4096 Dec  1 15:34 scripts
-rw-r--r-- 1 adam adam     1907 Dec  1 15:34 README.md
-rw-r--r-- 1 adam adam       88 Dec  1 15:34 Dockerfile
drwxr-xr-x 5 adam adam     4096 Dec  1 15:34 addons
-rw-r--r-- 1 adam adam      613 Dec  1 16:12 docker-compose.yml
-rw-r--r-- 1 adam adam 27954811 Dec  1 16:37 backup_20251201_163703.tar.gz


vs

adamb@picuas cprodoo % ls -lrt
total 242904
-rw-r--r--  1 adamb  staff  11858025 Nov 29 20:42 backup_20251129_204214.tar.gz
-rw-r--r--  1 adamb  staff  27704679 Nov 29 20:49 backup_20251129_194610.tar.gz
-rw-r--r--  1 adamb  staff  27716900 Dec  1 14:25 backup_20251201_132418.tar.gz
drwxr-xr-x  7 adamb  staff       224 Dec  1 14:52 addons
drwxr-xr-x  4 adamb  staff       128 Dec  1 15:00 scripts
-rw-r--r--  1 adamb  staff        88 Dec  1 15:03 Dockerfile
-rw-r--r--  1 adamb  staff      1907 Dec  1 16:31 README.md
-rw-r--r--  1 adamb  staff  27979075 Dec  1 16:33 backup_20251201_163303.tar.gz
-rw-r--r--  1 adamb  staff  27954811 Dec  1 17:40 backup_20251201_163703.tar.gz
-rw-r--r--  1 adamb  staff       613 Dec  1 17:50 docker-compose.yml
-rw-r--r--  1 adamb  staff         0 Dec  9 14:33 DEVLOG.md

Ok, looks like picuas is the latest.. Let's keep developing locally.

picuas% docker-compose up


Ok, stripe...  

Try with claude?

Let's install claude


Or should I use solveit?


Try solveit again.  I had a dialog there already.

Kind of slow to get started.


Actually solveit shows the last state.  so nice.

Settings / Stripe.

Click activate stripe.

Waht is my stripe account?

adam@code.pr

need the CPR EIN


Created a link for a Holberton grad membership. $24
https://buy.stripe.com/test_28E4gz1CV7q48H23A45c400

Virtual Office.
https://buy.stripe.com/test_eVq5kD3L3bGk8H2gmQ5c403

combo, hot desk plus virtual
https://buy.stripe.com/test_bJe7sLgxPh0E4qMdaE5c401

hot desk
https://buy.stripe.com/test_3cI8wPftL9yc1eA3A45c402

day pass
https://buy.stripe.com/test_7sYdR995naCg5uQb2w5c404

Trying to add these to the plans page. 

Ok, the stupid cards are not editing properly.  gpt suggested html mode in the odoo editor.

Let's try that.

nope.  none of that seems to work. i can't edit the fucking button.  odoo is not my friend tonight.

Added a day pass.  ran the stripe cli for webhooks

adamb@picuas ~ % stripe listen --forward-to localhost:8069/payment/stripe/webhook

> Ready! You are using Stripe API Version [2025-11-17.clover]. Your webhook signing secret is whsec_9a7ccb6394bfc1b82e1402507cc18a31a1d9d4085694e6d432fbac18d9b09fb8 (^C to quit)
2025-12-09 22:56:36   --> product.created [evt_1ScdZvFWEYN6JR6KFuETXzcj]
2025-12-09 22:56:36  <--  [200] POST http://localhost:8069/payment/stripe/webhook [evt_1ScdZvFWEYN6JR6KFuETXzcj]
2025-12-09 22:56:36   --> price.created [evt_1ScdZwFWEYN6JR6K6s4mMiVc]
2025-12-09 22:56:36  <--  [200] POST http://localhost:8069/payment/stripe/webhook [evt_1ScdZwFWEYN6JR6K6s4mMiVc]
2025-12-09 22:56:36   --> product.updated [evt_1ScdZwFWEYN6JR6KEZAjiXSU]
2025-12-09 22:56:36  <--  [200] POST http://localhost:8069/payment/stripe/webhook [evt_1ScdZwFWEYN6JR6KEZAjiXSU]
2025-12-09 22:59:16   --> product.updated [evt_1ScdcVFWEYN6JR6KFOBcfezf]
2025-12-09 22:59:16  <--  [200] POST http://localhost:8069/payment/stripe/webhook [evt_1ScdcVFWEYN6JR6KFOBcfezf]
2025-12-09 22:59:16   --> product.updated [evt_1ScdcWFWEYN6JR6KOtswEm3s]
2025-12-09 22:59:16  <--  [200] POST http://localhost:8069/payment/stripe/webhook [evt_1ScdcWFWEYN6JR6KOtswEm3s]
2025-12-09 23:01:15   --> payment_link.created [evt_1ScdeRFWEYN6JR6KHpdtfsGA]
2025-12-09 23:01:15  <--  [200] POST http://localhost:8069/payment/stripe/webhook [evt_1ScdeRFWEYN6JR6KHpdtfsGA]
2025-12-09 23:14:58   --> charge.succeeded [evt_3ScdrhFWEYN6JR6K2oeMH1JZ]
2025-12-09 23:14:58  <--  [200] POST http://localhost:8069/payment/stripe/webhook [evt_3ScdrhFWEYN6JR6K2oeMH1JZ]
2025-12-09 23:14:58   --> payment_intent.succeeded [evt_3ScdrhFWEYN6JR6K25PUzTEG]
2025-12-09 23:14:58  <--  [200] POST http://localhost:8069/payment/stripe/webhook [evt_3ScdrhFWEYN6JR6K25PUzTEG]
2025-12-09 23:14:58   --> payment_intent.created [evt_3ScdrhFWEYN6JR6K21A2tkMB]
2025-12-09 23:14:58  <--  [200] POST http://localhost:8069/payment/stripe/webhook [evt_3ScdrhFWEYN6JR6K21A2tkMB]
2025-12-09 23:14:58   --> checkout.session.completed [evt_1ScdriFWEYN6JR6K4jPxr4T7]
2025-12-09 23:14:58  <--  [200] POST http://localhost:8069/payment/stripe/webhook [evt_1ScdriFWEYN6JR6K4jPxr4T7]
2025-12-09 23:15:00   --> charge.updated [evt_3ScdrhFWEYN6JR6K2BJIoUr2]
2025-12-09 23:15:00  <--  [200] POST http://localhost:8069/payment/stripe/webhook [evt_3ScdrhFWEYN6JR6K2BJIoUr2]

## 2025-12-09

### Stripe Integration
- Created Stripe account for Code Puerto Rico
- Configured Stripe payment provider in Odoo (test mode)
- Created products:
  - Holberton Grad Membership: $10/month recurring subscription
  - Day Pass: $20 one-time purchase
- Added payment links to pricing page
- Tested webhooks using Stripe CLI (`stripe listen --forward-to localhost:8069/payment/stripe/webhook`)
- Confirmed webhooks received by Odoo (200 responses)

### Issue Found
- Built-in Stripe webhook handler doesn't create contacts from external payment links
- Started building custom webhook controller in cpr_membership module
- Files created: controllers/__init__.py, controllers/stripe_webhook.py
- Need to test and verify contact creation on checkout.session.completed

### Previous Sessions
- Google OAuth working (published, out of test mode)
- Production deployed at https://code.pr via Cloudflare Tunnel
- Backup/restore scripts working between Mac and Debian
