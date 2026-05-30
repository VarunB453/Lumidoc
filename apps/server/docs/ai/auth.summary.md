# Auth — AI Context Card

## Public surface
`POST  /api/v1/auth/register`          → `{user, tokens}`
`POST  /api/v1/auth/login`             → `{user, tokens}`
`POST  /api/v1/auth/refresh`           → `TokenPair` (rotates refresh token)
`POST  /api/v1/auth/logout`            → `MessageResponse` (idempotent)
`GET   /api/v1/auth/google`            → 302 to Google
`GET   /api/v1/auth/google/callback`   → 302 to frontend with tokens in URL fragment

## Token shape
RS256 JWTs. Access ≈ 15 min, refresh ≈ 7 days. Claims: `sub`, `email`, `type`, `jti`, `iat`, `exp`, `iss`, `aud`.

## Stores
- Mongo `users`: hashed_password (bcrypt), provider (`local`|`google`), avatar_url.
- Redis: `blacklist:{jti}` (revoked refresh), `session:{user_id}` (current refresh jti).

## Refresh-rotation flow
1. Decode refresh, verify `type="refresh"`, check `is_blacklisted(jti)`.
2. Blacklist old jti for its remaining TTL.
3. Issue new pair via `_issue_tokens`; store new session.

## Middleware
`AuthMiddleware` validates the access token on every request except `PUBLIC_PREFIXES` (auth/register, login, refresh, google, avatars, health, docs, openapi). Reads token from `Authorization: Bearer ...` **or** `?token=` (for SSE).

## Gotchas
- Redis outages are tolerated for blacklist *checks* (open-fail) but not for *writes* — failures are logged and swallowed.
- `oauth_login_or_create` creates a user with `hashed_password=None` for social sign-ins; password change endpoint blocks those accounts.
