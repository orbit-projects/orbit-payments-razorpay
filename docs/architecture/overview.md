# Razorpay adapter architecture

This package implements `orbit_payments.PaymentProvider` through Razorpay's Python SDK. The
capability owns the common protocol and models; this adapter owns Razorpay order/payment/refund
resources, API credentials, webhook verification, thread execution, and the SDK session lifecycle.

## Implemented operations

- `create_payment`: creates an Order using integer minor units, uppercase currency, merchant
  reference as the Razorpay receipt, and bounded metadata as notes.
- `get_payment`: retrieves an Order by its Razorpay Order ID.
- `refund`: creates a full or partial refund against a Razorpay Payment ID.
- `verify_webhook`: validates HMAC-SHA256 over the original raw body with the webhook secret before
  parsing and returning normalized metadata.
- `verify_checkout_signature`: verifies the Checkout response signature over `order_id|payment_id`
  with the API secret.

Razorpay's SDK is synchronous. Calls run in `asyncio.to_thread` and are bounded by a semaphore and
finite HTTP timeout. Cancellation waits for an in-progress SDK HTTP call to finish before capacity
is released; Python cannot forcibly terminate a synchronous request. Shutdown drains those calls
and closes the adapter-owned SDK session.

Razorpay's standard Orders API does not provide the same idempotency contract as Stripe's
PaymentIntent API. The adapter does not retry order creation automatically. `receipt` is a
merchant-side reconciliation reference, not a claim of exactly-once processing.
