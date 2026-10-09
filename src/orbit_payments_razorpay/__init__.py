# Copyright 2026-present Orbit Contributors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Razorpay adapter for Orbit Payments."""

from orbit_payments_razorpay.config import RazorpayConfig
from orbit_payments_razorpay.provider import RazorpayPaymentProvider

__all__ = ["RazorpayConfig", "RazorpayPaymentProvider"]
