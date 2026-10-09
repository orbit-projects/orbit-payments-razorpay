import hashlib
import hmac
import json
from types import SimpleNamespace
from typing import Any

import pytest

pytest.importorskip("razorpay")
from orbit_payments import PaymentRequest, PaymentWebhookError, RefundRequest

from orbit_payments_razorpay import RazorpayConfig, RazorpayPaymentProvider


def config() -> RazorpayConfig:
    return RazorpayConfig(key_id="key-id", key_secret="key-secret", webhook_secret="webhook-secret")


class FakeRazorpayClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple[Any, ...]]] = []
        self.order = SimpleNamespace(create=self.create_order, fetch=self.fetch_order)
        self.payment = SimpleNamespace(refund=self.create_refund)

    def create_order(self, payload: dict[str, Any]) -> dict[str, Any]:
        self.calls.append(("order.create", (payload,)))
        return {
            "id": "order_123",
            "amount": payload["amount"],
            "currency": payload["currency"],
            "status": "created",
            "receipt": payload["receipt"],
            "created_at": 1_780_000_000,
        }

    def fetch_order(self, order_id: str) -> dict[str, Any]:
        self.calls.append(("order.fetch", (order_id,)))
        return {
            "id": order_id,
            "amount": 100,
            "currency": "INR",
            "status": "paid",
            "receipt": "order-1",
        }

    def create_refund(self, payment_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        self.calls.append(("payment.refund", (payment_id, payload)))
        return {
            "id": "rfnd_123",
            "payment_id": payment_id,
            "amount": payload.get("amount", 100),
            "currency": "INR",
            "status": "processed",
        }


@pytest.mark.asyncio
async def test_create_retrieve_refund_and_drain() -> None:
    client = FakeRazorpayClient()
    provider = RazorpayPaymentProvider(config(), client=client)
    payment = await provider.create_payment(
        PaymentRequest(amount_minor=100, currency="INR", reference="order-1")
    )
    retrieved = await provider.get_payment("order_123")
    refund = await provider.refund(
        RefundRequest(payment_id="pay_123", reference="refund-1", amount_minor=50)
    )

    assert payment.provider_id == "order_123"
    assert payment.reference == "order-1"
    assert retrieved.status.value == "succeeded"
    assert refund.amount_minor == 50
    assert refund.status.value == "succeeded"
    assert [name for name, _ in client.calls] == [
        "order.create",
        "order.fetch",
        "payment.refund",
    ]
    await provider.aclose()


def test_webhook_checks_raw_signature_before_parsing_and_rejects_duplicate_keys() -> None:
    provider = RazorpayPaymentProvider(config(), client=FakeRazorpayClient())
    body = json.dumps({"event": "payment.captured", "created_at": 1_780_000_000}).encode()
    signature = hmac.new(b"webhook-secret", body, hashlib.sha256).hexdigest()
    event = provider.verify_webhook(body, signature)
    assert event.event_type == "payment.captured"
    assert event.event_id == hashlib.sha256(body).hexdigest()

    with pytest.raises(PaymentWebhookError):
        provider.verify_webhook(body, "0" * 64)

    duplicate_body = b'{"event":"payment.captured","event":"payment.failed"}'
    duplicate_signature = hmac.new(b"webhook-secret", duplicate_body, hashlib.sha256).hexdigest()
    with pytest.raises(PaymentWebhookError):
        provider.verify_webhook(duplicate_body, duplicate_signature)


def test_checkout_signature_matches_documented_order_payment_pair() -> None:
    provider = RazorpayPaymentProvider(config(), client=FakeRazorpayClient())
    message = b"order_123|pay_123"
    signature = hmac.new(b"key-secret", message, hashlib.sha256).hexdigest()
    assert provider.verify_checkout_signature("order_123", "pay_123", signature)
    assert not provider.verify_checkout_signature("order_123", "pay_other", signature)


@pytest.mark.asyncio
async def test_closed_provider_rejects_new_operations() -> None:
    provider = RazorpayPaymentProvider(config(), client=FakeRazorpayClient())
    await provider.aclose()
    with pytest.raises(RuntimeError):
        await provider.get_payment("order_123")
