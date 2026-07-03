from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import Blueprint, abort, current_app, g, jsonify, request

auth_bp = Blueprint("auth", __name__)


def generate_token(subject: str) -> str:
    """Genera un JWT HS256 firmado con ``JWT_SECRET`` para el subject dado."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "iat": now,
        "exp": now + timedelta(minutes=current_app.config["JWT_EXP_MINUTES"]),
    }
    return jwt.encode(payload, current_app.config["JWT_SECRET"], algorithm="HS256")


def jwt_required(fn):
    """
    Decorador que exige un JWT válido en el header Authorization (Bearer).
    """

    @wraps(fn)
    def wrapper(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            abort(401, description="Falta el token Bearer.")

        token = header.split(" ", 1)[1]
        try:
            payload = jwt.decode(
                token,
                current_app.config["JWT_SECRET"],
                algorithms=["HS256"],
            )
        except jwt.ExpiredSignatureError:
            abort(401, description="Token expirado.")
        except jwt.InvalidTokenError:
            abort(401, description="Token inválido.")

        g.jwt_subject = payload.get("sub")
        return fn(*args, **kwargs)

    return wrapper


@auth_bp.post("/auth/login")
def login():
    """
    Valida credenciales simples y devuelve un JWT.
    """
    body = request.get_json() or {}
    username = body.get("username")
    password = body.get("password")

    if (
        username != current_app.config["AUTH_USERNAME"]
        or password != current_app.config["AUTH_PASSWORD"]
    ):
        abort(401, description="Credenciales inválidas.")

    return jsonify({"token": generate_token(username)}), 200
