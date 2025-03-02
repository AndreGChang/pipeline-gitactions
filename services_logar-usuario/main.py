import functions_framework
import json
import firebase_admin
from firebase_admin import auth, credentials
from flask import request

# Inicializa Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred)

@functions_framework.http
def login_user(request):
    """Faz login do usuário e retorna um Token JWT."""

    cors_headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }

    if request.method == "OPTIONS":
        return "", 204, cors_headers

    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return json.dumps({"error": "Email e senha são obrigatórios"}), 400, cors_headers

        # Simula login e retorna um Token JWT
        user = auth.get_user_by_email(email)
        custom_token = auth.create_custom_token(user.uid)

        return json.dumps({"token": custom_token.decode("utf-8")}), 200, cors_headers

    except Exception as e:
        return json.dumps({"error": str(e)}), 500, cors_headers
