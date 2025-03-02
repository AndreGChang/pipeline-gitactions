import functions_framework
import json
import firebase_admin
from firebase_admin import auth, credentials
from flask import request

# Inicializa Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred)

def verificar_autenticacao():
    """Valida o token JWT do Firebase enviado no cabeçalho Authorization."""
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        return None, json.dumps({"error": "Token de autenticação ausente ou inválido"}), 401

    token = auth_header.split("Bearer ")[1]
    try:
        decoded_token = auth.verify_id_token(token)  # Firebase já valida e decodifica
        return decoded_token, None, 200  # Retorna os dados do usuário autenticado
    except Exception as e:
        return None, json.dumps({"error": "Token inválido ou expirado"}), 401

@functions_framework.http
def validate_token(request):
    """Verifica se o token JWT do Firebase é válido."""
    
    cors_headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
    }

    if request.method == "OPTIONS":
        return "", 204, cors_headers

    user, error_response, status = verificar_autenticacao()
    if not user:
        return error_response, status, cors_headers

    return json.dumps({"message": "Token válido", "user": user}), 200, cors_headers
