import functions_framework
import json
from datetime import datetime
from google.cloud import firestore
import firebase_admin
from firebase_admin import auth, credentials
from flask import request

# Inicializa Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred)

# Inicializa o cliente do Firestore
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
def atualizar_status_pedido(request):
    """Atualiza o status de um pedido no Firestore, apenas para usuários autenticados."""

    # Configuração CORS para permitir requisições do frontend
    cors_headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "OPTIONS, PUT, PATCH",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
    }

    # Responder pré-requisição (CORS)
    if request.method == "OPTIONS":
        return "", 204, cors_headers

    # Verifica se o usuário está autenticado
    user, error_response, status = verificar_autenticacao()
    if not user:
        return error_response, status, cors_headers

    if request.method not in ["PUT", "PATCH"]:
        return json.dumps({"error": "Método não permitido"}), 405, cors_headers

    try:
        # Extrai o ID do pedido da URL
        path = request.path.strip("/")
        partes = path.split("/")
        if len(partes) < 2 or partes[0] != "pedidos":
            return json.dumps({"error": "ID do pedido não fornecido corretamente"}), 400, cors_headers

        pedido_id = partes[1]

        # Obtém o corpo da requisição
        dados = request.get_json(silent=True)
        if not dados or "status" not in dados:
            return json.dumps({"error": "Nenhum dado válido enviado"}), 400, cors_headers

        # Busca o pedido no Firestore
        doc_ref = db.collection("pedidos").document(pedido_id)
        doc = doc_ref.get()

        if not doc.exists:
            return json.dumps({"error": "Pedido não encontrado"}), 404, cors_headers

        # Atualiza o status do pedido
        doc_ref.update({"status": dados["status"], "ultima_atualizacao": datetime.utcnow().isoformat() + "Z"})

        resposta = {
            "message": "Status do pedido atualizado com sucesso",
            "id": pedido_id,
            "status": dados["status"]
        }
        return json.dumps(resposta), 200, cors_headers

    except Exception as e:
        return json.dumps({"error": str(e)}), 500, cors_headers
