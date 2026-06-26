# backend/app

This folder contains the core backend package for your FastAPI application. It provides the Supabase admin client, authentication helper, and API routes used by the backend service.

## Package layout

- `__init__.py`
  - Empty file that makes `backend/app` a Python package.
  - It currently has no initialization logic, but its presence is required for relative imports within the package.

- `supabase_client.py`
  - Creates and exports a Supabase admin client instance named `supabase_admin`.
  - Loads environment variables from a `.env` file using `python-dotenv`.
  - Reads `SUPABASE_URL` and `SUPABASE_SERVICE_KEY`.
  - This client is used by the backend for admin-level operations such as user creation, login, and protected data fetching.

- `auth.py`
  - Defines the `verify_student_token` dependency used by protected routes.
  - Reads the HTTP `Authorization` header and expects a value in the form `Bearer <token>`.
  - Calls `supabase_admin.auth.get_user(token)` to validate the session token with Supabase.
  - If the token is missing, malformed, or invalid, it raises a `401 Unauthorized` response.

- `routes.py`
  - Defines FastAPI API routes grouped under `/api/v1`.
  - Uses `APIRouter` and `pydantic` models to validate request payloads.
  - Contains the following endpoints:
    - `POST /api/v1/auth/signup`
      - Creates a new Supabase user using `supabase_admin.auth.admin.create_user()`.
      - Also inserts a row in the `profiles` table with a `current_phase` value of `learning`.
    - `POST /api/v1/auth/login`
      - Signs in a user with email/password using `supabase_admin.auth.sign_in_with_password()`.
      - Returns an access token and the user ID on success.
    - `POST /api/v1/chat`
      - Protected route that requires a valid bearer token.
      - Uses `verify_student_token` to validate the user session.
      - Reads the user's `current_phase` from the `profiles` table.
      - Currently returns a dummy response; commented code shows where a Google ADK workflow could be executed.

## How this folder works together

- `supabase_client.py` builds the shared Supabase connection.
- `auth.py` imports that client and uses it to verify user tokens.
- `routes.py` imports both the client and the auth dependency.
- `routes.py` exports a FastAPI router object named `router`, which can be mounted on a FastAPI app in `main.py` or another startup module.

## How to use this package in the backend

1. Ensure environment variables are defined in `backend/.env` or the system environment:
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_KEY`

2. Add a FastAPI app entrypoint (for example, in `backend/main.py`):

```python
from fastapi import FastAPI
from app.routes import router

app = FastAPI()
app.include_router(router)
```

3. Run the backend with Uvicorn:

```bash
uvicorn backend.main:app --reload
```

4. Call the API endpoints:
   - `POST /api/v1/auth/signup` to create a new user
   - `POST /api/v1/auth/login` to sign in and receive an access token
   - `POST /api/v1/chat` to run the protected chat route with `Authorization: Bearer <token>`

## Notes and next steps

- The `chat` endpoint is currently a placeholder. The commented code suggests integrating a Google ADK workflow when ready.
- If you want to make this package more explicit, you can add `__all__ = ["router"]` to `app/__init__.py`.
- `routes.py` currently uses relative imports, which is the correct pattern for modules in this package.

## Troubleshooting

- If imports fail, make sure the `backend` folder is on Python path and that you run the app from the repository root.
- If `SUPABASE_URL` or `SUPABASE_SERVICE_KEY` are missing or invalid, Supabase client creation will fail.
- If VS Code shows yellow import warnings, open the workspace at `kamara_v0.1` and confirm `backend` is part of your Python path.
