from __future__ import annotations

API_DESCRIPTION = """
# Belong Investment API

Belong is a regulated investment platform for Kenya, operated by
Tradiam Investments Limited under CMA & DPC oversight. This API
powers the Belong mobile apps (iOS / Android).

**Base URL:** `https://api.belonginvest.com/api`
**Auth:** Bearer JWT (`Authorization: Bearer <access_token>`)

---

## Error Format

All errors follow a consistent envelope:

```json
{"error": {"code": "UPPER_SNAKE", "message": "...", "details": {}}}
```

Clients should switch on `code`, not `message`.

---

## 1 - Authentication

| Step | Method | Path |
|------|--------|------|
| Request OTP | POST | `/auth/otp/send` |
| Verify OTP | POST | `/auth/otp/verify` |
| Register | POST | `/auth/register` |
| Login | POST | `/auth/login` |
| Set PIN | POST | `/auth/pin/set` |
| Refresh token | POST | `/token/pair` |

Register and Login return `access` + `refresh` JWT tokens.
Access tokens expire in 15 min; refresh tokens in 30 days.

---

## 2 - Onboarding

| Step | Method | Path |
|------|--------|------|
| Update profile | PATCH | `/users/me` |
| Accept terms | POST | `/users/me/terms` |
| Start AI profiler | POST | `/ai-profiler/sessions/start` |
| Chat with profiler | POST | `/ai-profiler/sessions/{id}/message` |
| Complete profiling | POST | `/ai-profiler/sessions/{id}/complete` |
| Start KYC | POST | `/kyc/start` |
| Upload documents | POST | `/kyc/documents` |
| Upload selfie | POST | `/kyc/selfie` |

---

## 3 - Investing

| Step | Method | Path |
|------|--------|------|
| Browse funds | GET | `/funds/` |
| Fund detail | GET | `/funds/{id}` |
| Run projection | POST | `/funds/projection` |
| Create investment | POST | `/investments/` |
| Initiate payment | POST | `/payments/initiate/` |
| Track portfolio | GET | `/portfolio/` |
| View holdings | GET | `/portfolio/holdings` |

---

## 4 - Features

| Feature | Key Endpoints |
|---------|---------------|
| Goals | `POST /investment-goals/`, `GET /investment-goals/` |
| Recurring plans | `POST /recurring-plans/`, `GET /recurring-plans/` |
| Wishlist | `POST /wishlist/`, `GET /wishlist/` |
| Social feed | `POST /feed/posts`, `GET /feed/` |
| Referrals | `GET /referrals/my-code`, `GET /referrals/stats` |
| Notifications | `GET /notifications/`, `POST /notifications/push-token` |
| Simulation | `POST /simulation/calculate` |
| Market data | `GET /market/rates`, `GET /market/tickers` |
| Compliance | `GET /compliance/limits`, `POST /compliance/consent` |
| Withdrawals | `POST /withdrawals/`, `GET /withdrawals/` |
| Wallet | `GET /wallet/` |

---

## 5 - Profiles & Playlists

| Step | Method | Path |
|------|--------|------|
| List templates | GET | `/ai-profiler/templates` |
| List playlists | GET | `/playlists/` |
| Playlist detail | GET | `/playlists/{id}` |

**Flow:** Questionnaire -> AI investor type -> profile template -> playlist -> jams.
All three endpoints are public (`auth=None`).
"""
