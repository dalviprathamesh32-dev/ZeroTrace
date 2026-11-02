# ZeroTrace: self-destructing, client-side encrypted messages

A small web app for sharing a message once. The message is encrypted in your browser, the server stores only ciphertext, and the key never leaves the link.

![Architecture](docs/architecture.png)

## How it works

1. You type a message. The browser generates a random 256-bit key and encrypts the message with **AES-GCM** (WebCrypto API).
2. Only the ciphertext is sent to the server and stored in **Redis** with a time limit (default 1 hour).
3. You get a link like `/view.html?id=<id>#<key>`. The key sits after `#`, so browsers never send it to the server.
4. The receiver opens the link and clicks **Reveal**. The browser fetches the ciphertext, the server deletes it in the same step (atomic GET + DELETE), and the browser decrypts it locally.
5. Opening the link again returns "not found".

The Reveal button is deliberate: link-preview bots (Slack, WhatsApp) open links automatically, and fetching on page load would burn the message before the real recipient sees it.

## Run it

**Docker (recommended):**

```bash
docker compose up --build
```

Then open http://localhost:8000.

**Local development:**

```bash
python -m venv myenv && source myenv/bin/activate
pip install -r requirements.txt
cp backend/.env.example backend/.env
# Redis must be running on localhost:6379
cd backend && uvicorn app.main:app --reload
```

## API

| Method | Path | Body | Response |
|---|---|---|---|
| POST | `/message` | `{"ciphertext": "<string, max 20000 chars>"}` | `{"id": "<id>"}` |
| GET | `/message/{id}` | | `{"ciphertext": "..."}` or `404` |
| GET | `/health` | | `{"message": "all ok"}` |

## Project structure

```
backend/app/
  main.py        app setup, routers, static frontend
  db.py          Redis connection
  core/          settings (.env) and CORS setup
  routes/        HTTP layer only
  schemas/       request validation (Pydantic)
  services/      Redis logic
frontend/        plain HTML, CSS and JS (no framework, no third-party scripts)
```

Routes never talk to Redis directly and services know nothing about HTTP.

## Configuration

Settings come from environment variables or `backend/.env` (see `backend/.env.example`). CORS is off by default because the frontend is served by the same app. To use a separate frontend origin, set `CORS_ORIGINS` as a JSON list.

## Tests

```bash
cd backend && pytest -v
```

Tests use an in-memory fake Redis. They cover creating a message, reading it once, a second read returning 404, unknown ids, and oversize or empty input.

## Threat model and limitations

What it protects against: someone reading stored data (a database leak shows only ciphertext) and the message lingering after it is read.

What it does not do:

- **You still trust the JavaScript the server sends.** A compromised server could ship code that steals the key. Strict CSP and no third-party scripts reduce this but do not remove it.
- **The server sees metadata**: IP address, message size and timing. This is not full anonymity.
- **Anyone with the full link can read the message once.** Share it over a channel you trust.
- Redis may write data to disk depending on its configuration, so "deleted" is not forensic-grade.
- No rate limiting, authentication or abuse reporting yet. Do not expose this version publicly as a service.
- Text messages only.

## Roadmap

- **v2:** rate limiting, security headers (CSP), hardened Redis config, HTTPS deployment, and a self-attack write-up
- **v3:** encrypted file sharing, audit logging, password-protected links

## Built by

Prathamesh Dalvi. Feedback and attack ideas are welcome via issues.

