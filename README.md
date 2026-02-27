# 🚆 IRTC Mini — Train Booking API

A simplified IRCTC-style backend built with **Django REST Framework**, featuring JWT authentication, train seat booking with concurrency control, and search analytics powered by MongoDB.

## Tech Stack

| Layer          | Technology                         |
| -------------- | ---------------------------------- |
| Framework      | Django 6 + Django REST Framework   |
| Auth           | JWT via `djangorestframework-simplejwt` |
| Primary DB     | MySQL 9 (transactional data)       |
| Analytics DB   | MongoDB 8 (search logs)            |
| API Docs       | OpenAPI 3 via `drf-spectacular`    |
| Server         | Gunicorn                           |
| Containerisation | Docker + Docker Compose          |

## Architecture

```
accounts/       → User registration & JWT login (email-based auth)
trains/         → Train CRUD (admin) & public search with filtering
bookings/       → Seat booking with select_for_update() concurrency control
analytics/      → Search-log middleware → MongoDB, top-routes aggregation
config/         → Settings, URL routing, DB router (MySQL ↔ MongoDB)
```

---

## Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) & [Docker Compose](https://docs.docker.com/compose/install/)

### 1. Clone the repository

```bash
git clone https://github.com/mjishnu/irtc-mini.git
cd irtc-mini
```

### 2. Create the environment file

```bash
cp .env.example .env
```

Edit `.env` and set secure values:

```dotenv
# Django
DJANGO_SECRET_KEY=your-random-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# MySQL
MYSQL_DATABASE=irtc_db
MYSQL_USER=irtc_user
MYSQL_PASSWORD=your-mysql-password
MYSQL_ROOT_PASSWORD=your-root-password
MYSQL_HOST=db
MYSQL_PORT=3306

# MongoDB
MONGO_DB_NAME=irtc_logs
MONGO_HOST=mongo
MONGO_PORT=27017
```

### 3. Build & start the containers

```bash
docker compose up --build -d
```

This starts three services:

| Service | Container      | Port  |
| ------- | -------------- | ----- |
| Django  | `irtc_web`     | 8000  |
| MySQL   | `irtc_mysql`   | 3306  |
| MongoDB | `irtc_mongo`   | 27017 |

The entrypoint script automatically runs migrations (MySQL + MongoDB) and collects static files before starting Gunicorn.

### 4. Verify the services

```bash
# Check container status
docker compose ps

# View Django logs
docker compose logs -f web
```

Once running, the API is available at `http://localhost:8000`.

### 5. Interactive API docs

| UI      | URL                                  |
| ------- | ------------------------------------ |
| Swagger | http://localhost:8000/api/docs/      |
| ReDoc   | http://localhost:8000/api/redoc/     |
| Schema  | http://localhost:8000/api/schema/    |

---

## API Reference & Sample Calls

> All examples use `curl`. Replace `localhost:8000` with your host if different.

### Accounts

#### Register a new user

```bash
curl -X POST http://localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "password": "SecurePass123!",
    "password2": "SecurePass123!",
    "phone_number": "9876543210"
  }'
```

**Response** `201 Created`

```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com",
  "phone_number": "9876543210",
  "date_of_birth": null,
  "tokens": {
    "refresh": "eyJ...",
    "access": "eyJ..."
  }
}
```

#### Login

```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123!"
  }'
```

**Response** `200 OK`

```json
{
  "email": "john@example.com",
  "role": "user",
  "tokens": {
    "refresh": "eyJ...",
    "access": "eyJ..."
  }
}
```

#### Refresh Token

Get a new access token using your refresh token.

```bash
curl -X POST http://localhost:8000/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "<your_refresh_token>"
  }'
```

**Response** `200 OK`

```json
{
  "access": "eyJ...",
  "refresh": "eyJ..."
}
```

> 💡 Save the `access` token — you'll need it as `Bearer <token>` for authenticated endpoints.

---

### Trains

#### Create a train _(admin only)_

```bash
curl -X POST http://localhost:8000/api/trains/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <admin_access_token>" \
  -d '{
    "train_number": "12301",
    "name": "Rajdhani Express",
    "source": "New Delhi",
    "destination": "Mumbai Central",
    "departure_time": "2026-03-15T06:00:00+05:30",
    "arrival_time": "2026-03-15T22:30:00+05:30",
    "total_seats": 500,
    "available_seats": 500
  }'
```

**Response** `201 Created`

```json
{
  "id": 1,
  "train_number": "12301",
  "name": "Rajdhani Express",
  "source": "New Delhi",
  "destination": "Mumbai Central",
  "departure_time": "2026-03-15T06:00:00+05:30",
  "arrival_time": "2026-03-15T22:30:00+05:30",
  "total_seats": 500,
  "available_seats": 500
}
```

#### Get / Update a train _(admin only)_

```bash
# Retrieve
curl http://localhost:8000/api/trains/1/ \
  -H "Authorization: Bearer <admin_access_token>"

# Partial update
curl -X PATCH http://localhost:8000/api/trains/1/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <admin_access_token>" \
  -d '{"available_seats": 480}'
```

#### Search trains _(public)_

```bash
# Search by source and destination
curl "http://localhost:8000/api/trains/search/?source=Delhi&destination=Mumbai"

# Search by date
curl "http://localhost:8000/api/trains/search/?date=2026-03-15"

# With pagination
curl "http://localhost:8000/api/trains/search/?source=Delhi&limit=5&offset=0"
```

**Response** `200 OK`

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "train_number": "12301",
      "name": "Rajdhani Express",
      "source": "New Delhi",
      "destination": "Mumbai Central",
      "departure_time": "2026-03-15T06:00:00+05:30",
      "arrival_time": "2026-03-15T22:30:00+05:30",
      "total_seats": 500,
      "available_seats": 500
    }
  ]
}
```

---

### Bookings

#### Book seats _(authenticated)_

```bash
curl -X POST http://localhost:8000/api/bookings/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d '{
    "train": 1,
    "seats_booked": 2
  }'
```

**Response** `201 Created`

```json
{
  "id": 1,
  "pnr": "A3B8D1C2E4",
  "train": 1,
  "seats_booked": 2,
  "status": "CONFIRMED",
  "booking_time": "2026-03-10T14:30:00+05:30"
}
```

> The API uses `select_for_update()` to prevent race conditions during concurrent bookings. Bookings for departed trains are rejected.

#### View my bookings _(authenticated)_

```bash
curl http://localhost:8000/api/bookings/my/ \
  -H "Authorization: Bearer <access_token>"
```

**Response** `200 OK`

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "pnr": "A3B8D1C2E4",
      "train": {
        "id": 1,
        "train_number": "12301",
        "name": "Rajdhani Express",
        "source": "New Delhi",
        "destination": "Mumbai Central",
        "departure_time": "2026-03-15T06:00:00+05:30",
        "arrival_time": "2026-03-15T22:30:00+05:30",
        "total_seats": 500,
        "available_seats": 498
      },
      "seats_booked": 2,
      "status": "CONFIRMED",
      "booking_time": "2026-03-10T14:30:00+05:30"
    }
  ]
}
```

---

### Analytics

#### Top searched routes _(public)_

```bash
curl http://localhost:8000/api/analytics/top-routes/
```

**Response** `200 OK`

```json
[
  { "source": "New Delhi", "destination": "Mumbai Central", "search_count": 42 },
  { "source": "Bangalore", "destination": "Chennai", "search_count": 28 },
  { "source": "Kolkata", "destination": "New Delhi", "search_count": 15 }
]
```

> Search requests to `/api/trains/search/` are automatically logged to MongoDB (fire-and-forget) via middleware. This endpoint aggregates those logs.

---

## Endpoint Summary

| Method | Endpoint                      | Auth       | Description                        |
| ------ | ----------------------------- | ---------- | ---------------------------------- |
| POST   | `/api/register/`              | None       | Register a new user                |
| POST   | `/api/login/`                 | None       | Login and receive JWT tokens       |
| POST   | `/api/token/refresh/`         | None       | Get new access token using refresh |
| POST   | `/api/trains/`                | Admin JWT  | Create a new train                 |
| GET    | `/api/trains/<id>/`           | Admin JWT  | Retrieve train details             |
| PUT    | `/api/trains/<id>/`           | Admin JWT  | Full update a train                |
| PATCH  | `/api/trains/<id>/`           | Admin JWT  | Partial update a train             |
| GET    | `/api/trains/search/`         | None       | Search trains (filterable)         |
| POST   | `/api/bookings/`              | User JWT   | Book seats on a train              |
| GET    | `/api/bookings/my/`           | User JWT   | View authenticated user's bookings |
| GET    | `/api/analytics/top-routes/`  | None       | Top 5 most-searched routes         |

## Environment Variables

| Variable              | Default              | Description                    |
| --------------------- | -------------------- | ------------------------------ |
| `DJANGO_SECRET_KEY`   | _(insecure fallback)_| Django secret key              |
| `DJANGO_DEBUG`        | `False`              | Enable debug mode              |
| `DJANGO_ALLOWED_HOSTS`| `localhost`          | Comma-separated allowed hosts  |
| `MYSQL_DATABASE`      | `irtc_db`            | MySQL database name            |
| `MYSQL_USER`          | `irtc_user`          | MySQL user                     |
| `MYSQL_PASSWORD`      | `irtc_pass_123`      | MySQL password                 |
| `MYSQL_ROOT_PASSWORD` | `root_pass_123`      | MySQL root password            |
| `MYSQL_HOST`          | `db`                 | MySQL host (Docker service)    |
| `MYSQL_PORT`          | `3306`               | MySQL port                     |
| `MONGO_DB_NAME`       | `irtc_logs`          | MongoDB database name          |
| `MONGO_HOST`          | `mongo`              | MongoDB host (Docker service)  |
| `MONGO_PORT`          | `27017`              | MongoDB port                   |

## License

[MIT](LICENSE)
