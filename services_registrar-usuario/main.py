import functions_framework
import json
import firebase_admin
from firebase_admin import auth, credentials
from flask import request

# Inicializa Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.ApplicationDefault()  # Usa credenciais do ambiente
    firebase_admin.initialize_app(cred)

@functions_framework.http
def register_user(request):
    """Registra um novo usuário com e-mail e senha no Firebase Authentication."""

    # Configuração CORS
    cors_headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }

    # Responder preflight requests (CORS)
    if request.method == "OPTIONS":
        return "", 204, cors_headers

    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return json.dumps({"error": "Email e senha são obrigatórios"}), 400, cors_headers

        user = auth.create_user(email=email, password=password)

        return json.dumps({"message": "Usuário criado com sucesso", "uid": user.uid}), 201, cors_headers

    except Exception as e:
        return json.dumps({"error": str(e)}), 500, cors_headers
