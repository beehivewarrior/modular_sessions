# Modular-Sessions
Modular Sessions provides modular sessions management middleware for use with FastAPI.
This project takes its inspiration from [FastAPI-Sessions](https://github.com/jordanisaacs/fastapi-sessions) which is 
a great project but appears to not maintained anymore. Additionally, this project the project seeks to provide more
options for server-side session storage and session management like [Flask-Sessions](https://github.com/fengsp/flask-session).

---

Source Code: [https://github.com/beehivewarrior/modular_sessions/](https://github.com/beehivewarrior/modular_sessions/)

---

## Features

- [x] ASGI Compatible Middleware
- [x] Backend Agnostic with built-in support for Redis, and In-Memory
- [x] Frontend Agnostic with built-in support for Cookies, and Headers
- [x] Session Verification and Validation options
- [x] Pydantic Models for Session and Session Data

Built-in support for:
- Backends:
  - [x] Redis
  - [x] In-Memory
  - [ ] Memcached (Coming Soon)

- Frontends:
  - [x] Signed Cookies
  - [ ] Headers (Coming Soon)

- Verification:
  - [x] Basic
  - [ ] Okta (Coming Soon)