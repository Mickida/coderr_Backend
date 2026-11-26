# Coderr Backend

REST API for Coderr, a freelancer marketplace. Built with Django and
Django REST Framework.

- **Live demo:** https://coderr.daniel-micklausch.de
- **API:** https://mickida.pythonanywhere.com/api/
- **Frontend:** [coderr_Frontend](https://github.com/Mickida/coderr_Frontend)

Developed as part of the Developer Akademie GmbH training program.

## Setup

1. Clone the repository:

```bash
git clone <repository-url>
```

2. Change into the project folder:

```bash
cd coderr_Backend
```

3. Create a virtual environment:

```bash
python -m venv venv
```

4. Activate it on Windows:

```bash
venv\Scripts\activate
```

or on macOS / Linux:

```bash
source venv/bin/activate
```

5. Install the dependencies:

```bash
pip install -r requirements.txt
```

6. Copy `.env.example` to `.env` and set `SECRET_KEY`. A secret key
   can be generated with:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

7. Create the database tables:

```bash
python manage.py migrate
```

8. Start the server:

```bash
python manage.py runserver
```

The API runs at `http://127.0.0.1:8000/api/`. The frontend is a separate
project; by default CORS allows `http://127.0.0.1:5500` and
`http://localhost:5500`.

## Environment variables

| Variable           | Default                                       | Description                                        |
| ------------------ | --------------------------------------------- | -------------------------------------------------- |
| `SECRET_KEY`       | – (required)                                  | Django secret key                                  |
| `DEBUG`            | `False`                                       | `True` for local development                       |
| `ALLOWED_HOSTS`    | `localhost,127.0.0.1`                         | Comma-separated host names of the backend          |
| `FRONTEND_ORIGINS` | `http://127.0.0.1:5500,http://localhost:5500` | Comma-separated frontend origins for CORS and CSRF |

## Deployment (PythonAnywhere)

1. Clone the repository in a Bash console, create the virtual environment
   and install the dependencies as described in the setup.
2. Create `.env` with a new `SECRET_KEY`, `DEBUG=False`,
   `ALLOWED_HOSTS=<username>.pythonanywhere.com` and
   `FRONTEND_ORIGINS=https://<your-frontend-domain>`.
3. Create the database tables:

```bash
python manage.py migrate
```

4. Collect the static files (admin, browsable API):

```bash
python manage.py collectstatic
```

5. In the _Web_ tab, create a manual configuration web app, set the
   virtualenv path and point the WSGI file to `core.wsgi`.
6. Add two static file mappings in the _Web_ tab: `/static/` →
   `<project>/static` and `/media/` → `<project>/media`.
7. Reload the web app.

## Guest logins

The frontend's guest login buttons expect these users. The database
starts empty, so register them once (e.g. via the frontend or
`POST /api/registration/`):

| Username | Password | Type     |
| -------- | -------- | -------- |
| `daniel` | `asdasd` | customer |
| `kevin`  | `asdasd` | business |

## Notes

- Authentication: `Authorization: Token <token>`; login uses the
  username.
- An invalid token is rejected with 401, even on `/api/login/`. After a
  database reset, log out in the frontend first.
- The offer list (`GET /api/offers/`) and `GET /api/base-info/` are
  public; all other read endpoints require authentication.
- The offer list is paginated with 6 offers per page (`?page_size=`
  overrides it).
- Uploaded images (profile `file`, offer `image`) may be at most 5 MB.
  They are stored in `media/` and served by Django only while
  `DEBUG=True`; in production the web server serves them.
- The project's own test suite is not part of this repository.
