# Using RevenueCat webhooks to let AI agents trigger lifecycle automation

## Why this matters
Agent builders need subscription infrastructure that can be integrated and tested quickly. RevenueCat reduces launch friction while preserving analytics quality.

## Step-by-step implementation

1. Configure products in RevenueCat dashboard.
2. Initialize SDK and fetch offerings.
3. Present paywall and purchase flow.
4. Send webhook events into your automation pipeline.

```python
from revenuecat_agent import BillingClient

client = BillingClient(api_key="rc_live_xxx")
offerings = client.get_offerings(app_user_id="agent-user-123")
decision = client.select_offering(offerings, strategy="highest_expected_ltv")
purchase = client.purchase(package_id=decision.package_id)
print(purchase.status)
```

## Metrics to track
- Trial start rate
- Paywall conversion rate
- D7 retention for subscribers
- Refund rate by product

## Pitfalls
- Shipping paywalls without instrumentation
- Ignoring restore-purchase and entitlement edge cases
- Mixing test and production product IDs

## Next action
Run one A/B paywall copy test this week and evaluate conversion + refund deltas together.
