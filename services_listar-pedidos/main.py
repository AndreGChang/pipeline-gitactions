import functions_framework
import json
import firebase_admin
from firebase_admin import auth, credentials
from google.cloud import firestore
from flask import request

# Inicializa Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred)

# Inicializa o Firestore
db = firestore.Client()

def verificar_autenticacao():
    """Valida o token JWT do Firebase enviado no cabeçalho Authorization."""
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        return None, json.dumps({"error": "Token de autenticação ausente ou inválido"}), 401

    token = auth_header.split("Bearer ")[1]

    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token, None, 200  # Usuário autenticado com sucesso
    except Exception as e:
        return None, json.dumps({"error": "Token inválido ou expirado"}), 401


@functions_framework.http
def listar_pedidos(request):
    """Lista todos os pedidos cadastrados no Firestore, apenas para usuários autenticados."""

    # Configuração CORS para permitir requisições do frontend
    cors_headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
    }

    # Responder pré-requisição (CORS)
    if request.method == "OPTIONS":
        return "", 204, cors_headers

    # Verifica se o usuário está autenticado
    user, error_response, status = verificar_autenticacao()
    if not user:
        return error_response, status, cors_headers

    try:
        # Apenas permite requisições GET
        if request.method != "GET":
            return json.dumps({"error": "Método não permitido"}), 405, cors_headers

        # Buscar pedidos no Firestore
        pedidos_ref = db.collection("pedidos").stream()
        pedidos = []

        for doc in pedidos_ref:
            pedido_data = doc.to_dict()
            pedidos.append({
                "id": doc.id,
                "status": pedido_data.get("status", "DESCONHECIDO"),
                "total": pedido_data.get("total", 0.0),
                "data_criacao": pedido_data.get("data_criacao", ""),
                "cliente": pedido_data.get("cliente", ""),
                "email": pedido_data.get("email", ""),
                "itens": pedido_data.get("itens", []),
            })

        # Retorna os pedidos para o usuário autenticado
        return json.dumps(pedidos), 200, cors_headers

    except Exception as e:
        return json.dumps({"error": str(e)}), 500, cors_headers
