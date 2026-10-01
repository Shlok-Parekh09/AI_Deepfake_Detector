## 2024-05-24 - Fix Server-Side Request Forgery in Proxy Media
**Vulnerability:** Unauthenticated `proxy_media` endpoint allowed fetching arbitrary local files/internal network URLs because it proxied requests without validating if the destination IP is public.
**Learning:** Found an unused SSRF protection helper (`_is_safe_public_url`) in the `URLDownloader` class. Refactored it into a static method to use it directly in API routes.
**Prevention:** Always validate and filter user-supplied URLs against an allowlist or ensure they resolve to safe public IP space before proxying them using a backend client (like `httpx`).
