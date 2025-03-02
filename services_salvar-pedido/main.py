import functions_framework
import json
from datetime import datetime
import uuid
import firebase_admin
from firebase_admin import auth, credentials
from google.cloud import firestore
from flask import request

# Inicializa Firebase Admin SDK (se ainda não estiver inicializado)
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
def salvar_pedido(request):
    """Salva um pedido no Firestore apenas para usuários autenticados."""

    # Headers de CORS
    cors_headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization",
    }

    # Se for uma requisição OPTIONS (preflight), responde com CORS sem processamento
    if request.method == "OPTIONS":
        return ("", 204, cors_headers)

    # 🔒 Verifica se o usuário está autenticado
    user, error_response, status = verificar_autenticacao()
    if not user:
        return error_response, status, cors_headers

    try:
        # Verifica se o método é POST
        if request.method != "POST":
            return (json.dumps({"error": "Método não permitido"}), 405, cors_headers)
        
        # Decodifica o JSON recebido
        pedido = request.get_json(silent=True)
        if pedido is None:
            return (json.dumps({"error": "JSON inválido ou não fornecido"}), 400, cors_headers)

        # Valida os campos obrigatórios
        if "cliente" not in pedido or "email" not in pedido or "itens" not in pedido:
            return (json.dumps({"error": "Campos obrigatórios faltando"}), 400, cors_headers)

        # Calcula o total do pedido
        total = sum(item["quantidade"] * item["preco"] for item in pedido["itens"])

        # Cria o objeto a ser salvo
        pedido_salvo = {
            "id": str(uuid.uuid4()),
            "status": "PENDENTE",
            "total": total,
            "data_criacao": datetime.utcnow().isoformat() + "Z",
            "cliente": pedido["cliente"],
            "email": pedido["email"],
            "itens": pedido["itens"],
            "user_id": user["uid"],  # 🔥 Associa o pedido ao usuário autenticado
        }

        # Salva o pedido no Firestore
        doc_ref = db.collection("pedidos").document(pedido_salvo["id"])
        doc_ref.set(pedido_salvo)

        # Retorna sucesso
        response = json.dumps({
            "message": "Pedido criado com sucesso!",
            "id": pedido_salvo["id"],
            "status": pedido_salvo["status"],
            "total": pedido_salvo["total"],
            "data_criacao": pedido_salvo["data_criacao"]
        })

        return (response, 200, cors_headers)

    except Exception as e:
        return (json.dumps({"error": str(e)}), 500, cors_headers)
