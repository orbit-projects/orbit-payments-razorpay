# Razorpay adapter security

- API and webhook secrets are required and masked in configuration representations. There are no
  default credentials.
- Verify webhooks with HMAC-SHA256 over the exact raw body and compare signatures in constant time.
- Verify Checkout response signatures server-side with `verify_checkout_signature`; do not trust a
  browser success callback alone.
- Never log raw webhook bodies, credentials, SDK errors, or full provider responses.
- Keep API secrets on the server. Use the Order ID as the client-side checkout reference only
  after application authorization.
- Orbit does not handle raw card data or establish PCI compliance for the application.

See the repository [security policy](../../SECURITY.md) to report a vulnerability.
