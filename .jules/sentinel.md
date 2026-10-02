## 2024-05-24 - Fix Server-Side Request Forgery in Proxy Media
**Vulnerability:** Unauthenticated `proxy_media` endpoint allowed fetching arbitrary local files/internal network URLs because it proxied requests without validating if the destination IP is public.
**Learning:** Found an unused SSRF protection helper (`_is_safe_public_url`) in the `URLDownloader` class. Refactored it into a static method to use it directly in API routes.
**Prevention:** Always validate and filter user-supplied URLs against an allowlist or ensure they resolve to safe public IP space before proxying them using a backend client (like `httpx`).
## 2026-10-02 - [Error Leakage]\n**Vulnerability:** The API returned raw stack traces and internal error messages in 500/400 HTTP responses.\n**Learning:** Unhandled exceptions exposed server details via `traceback.format_exc()` directly to clients.\n**Prevention:** Catch generic exceptions and return sanitized messages, logging the full traceback only server-side.
