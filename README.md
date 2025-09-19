Got it! Here's a clean and focused `README.md` file that documents your project **as a website backend** (e.g., for user registration, login, profile management, etc.), without discussing the SMS transaction parsing logic:

```markdown
# drf-user-api

## Overview

**drf-user-api** is a Django REST Framework-based backend template that supports core user authentication features for any modern web or mobile application. This project can be integrated with a frontend (e.g., React, Vue, Flutter) to build a full-stack web platform.

It is ideal for use in websites requiring user account creation, secure login, password recovery, and profile management.

---

## Features

- ✅ User registration
- ✅ Secure login using JWT or session authentication
- ✅ Authenticated profile view & update
- ✅ Forgot password (send reset email or token)
- ✅ Reset password using token
- 🔒 Built with Django REST Framework for scalability and security

---

## Use Case

This project is intended to be used as the backend of a web application. You can integrate it with:
- A **React** frontend
- An **admin panel** or **dashboard**
- Any client needing user authentication APIs

---

## Project Structure

```

drf_api/
├── api/              # User registration, login, profile APIs
├── manage.py
├── requirements.txt
├── .env                # Environment variables (not committed)
├── drf_api\       # Project settings and root URLs
└── README.md

````

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/drf-user-api.git
cd drf-user-api
````

### 2. Set up the virtual environment

```bash
python -m venv env
source env/bin/activate  # or env\Scripts\activate on Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply migrations and start the server

```bash
python manage.py migrate
python manage.py runserver
```

---

## Environment Variables

Create a `.env` file to store your sensitive data:

```
DATABASE_URL=postgres://mlekwa:mlekwa123@localhost:5432/_db
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_USE_TLS=True
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=

STRIPE_TEST_API_KEY=p
STRIPE_TEST_SECRET_KEY=

# Database
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=


OPENROUTER_API_KEY=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

Use `python-decouple` or `django-environ` to manage `.env` variables securely in production.

---

## API Endpoints Summary

| Method | Endpoint                | Description            |
| ------ | ----------------------- | ---------------------- |
| POST   | `/users/register/`        | Register new user      |
| POST   | `/users/login/`           | User login             |
| GET    | `/users/profile/`         | Get user profile       |
| PUT    | `/users/profile/`         | Update user profile    |
| POST   | `/users/forgot-password/` | Request password reset |
| POST   | `/users/reset-password/`  | Submit new password    |

---

## License

This project is open source and available under the [MIT License](LICENSE).

---

## Author

Developed by \[Fine DR] – feel free to reach out for questions or collaboration!

```

Let me know if you want this saved as a file or want a `requirements.txt` generated too.
```
