# Coderr Backend

REST API for Coderr, a freelancer marketplace. Built with Django and
Django REST Framework.

## Setup

```bash
git clone <repository-url>
cd coderr_Backend
python -m venv venv
venv\Scripts\activate          # macOS / Linux: source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file with a secret key:

```bash
python -c "from django.core.management.utils import get_random_secret_key as key; open('.env', 'w').write('SECRET_KEY=' + key() + '\n')"
```

Set up the database and start the server:

```bash
python manage.py migrate
python manage.py runserver
```

The API runs at `http://127.0.0.1:8000/api/`. The frontend is a separate
project; CORS allows `http://127.0.0.1:5500` and `http://localhost:5500`.

## Guest logins

The frontend's guest login buttons expect these users. The database
starts empty, so register them once (e.g. via the frontend or
`POST /api/registration/`):

| Username | Password | Type |
|---|---|---|
| `daniel` | `asdasd` | customer |
| `kevin` | `asdasd` | business |

## Notes

- Authentication: `Authorization: Token <token>`; login uses the
  username.
- An invalid token is rejected with 401, even on `/api/login/`. After a
  database reset, log out in the frontend first.
