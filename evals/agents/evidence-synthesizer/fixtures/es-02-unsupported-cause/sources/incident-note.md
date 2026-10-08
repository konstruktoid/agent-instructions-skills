# Incident 2026-09-02: checkout unavailable

Written by the on-call engineer at 10:05.

Checkout returned errors for customers from 09:14 to 09:52. The root cause was a DNS
failure: the checkout service could not resolve `checkout-api.internal`, so every request
to it failed. The resolver was restarted at 09:50 and the service recovered.
