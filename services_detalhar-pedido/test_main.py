import unittest
import json
from unittest.mock import patch, MagicMock
from flask import Flask, Request
from main import obter_pedido

class TestObterPedido(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.client = self.app.test_client()

    @patch("main.verificar_autenticacao")
    def test_obter_pedido_sem_autenticacao(self, mock_verificar_autenticacao):
        """Testa se a função retorna erro quando o usuário não está autenticado"""
        mock_verificar_autenticacao.return_value = (None, json.dumps({"error": "Token de autenticação ausente ou inválido"}), 401)

        with self.app.test_request_context('/pedidos/123', method="GET"):
            response = obter_pedido(Request.from_values())
        
        self.assertEqual(response[1], 401)
        self.assertIn("Token de autenticação ausente ou inválido", response[0])

    @patch("main.verificar_autenticacao")
    def test_obter_pedido_metodo_nao_permitido(self, mock_verificar_autenticacao):
        """Testa se a função retorna erro quando o método HTTP não é GET"""
        mock_verificar_autenticacao.return_value = ({"uid": "user123"}, None, 200)

        with self.app.test_request_context('/pedidos/123', method="POST"):
            response = obter_pedido(Request.from_values())
        
        self.assertEqual(response[1], 405)
        self.assertIn("Método não permitido", response[0])

    @patch("main.verificar_autenticacao")
    @patch("main.db.collection")
    def test_obter_pedido_sucesso(self, mock_db_collection, mock_verificar_autenticacao):
        """Testa se a função retorna os detalhes de um pedido com sucesso"""
        mock_verificar_autenticacao.return_value = ({"uid": "user123"}, None, 200)

        # Simula um documento existente no Firestore
        mock_doc = MagicMock()
        mock_doc.exists = True
        mock_doc.to_dict.return_value = {"status": "enviado", "valor": 100.0}
        mock_doc_ref = MagicMock()
        mock_doc_ref.get.return_value = mock_doc
        mock_db_collection.return_value.document.return_value = mock_doc_ref

        with self.app.test_request_context('/pedidos/123', method="GET"):
            response = obter_pedido(Request.from_values())
        
        self.assertEqual(response[1], 200)
        self.assertIn("status", response[0])
        self.assertIn("valor", response[0])
        self.assertIn("id", response[0])

    @patch("main.verificar_autenticacao")
    @patch("main.db.collection")
    def test_obter_pedido_nao_encontrado(self, mock_db_collection, mock_verificar_autenticacao):
        """Testa se a função retorna erro ao tentar obter um pedido inexistente"""
        mock_verificar_autenticacao.return_value = ({"uid": "user123"}, None, 200)

        # Simula um documento que não existe
        mock_doc = MagicMock()
        mock_doc.exists = False
        mock_doc_ref = MagicMock()
        mock_doc_ref.get.return_value = mock_doc
        mock_db_collection.return_value.document.return_value = mock_doc_ref

        with self.app.test_request_context('/pedidos/123', method="GET"):
            response = obter_pedido(Request.from_values())
        
        self.assertEqual(response[1], 404)
        self.assertIn("Pedido não encontrado", response[0])

    @patch("main.verificar_autenticacao")
    def test_obter_pedido_id_invalido(self, mock_verificar_autenticacao):
        """Testa se a função retorna erro quando o ID do pedido não está correto na URL"""
        mock_verificar_autenticacao.return_value = ({"uid": "user123"}, None, 200)

        with self.app.test_request_context('/pedidos', method="GET"):
            response = obter_pedido(Request.from_values())
        
        self.assertEqual(response[1], 400)
        self.assertIn("ID do pedido não fornecido corretamente", response[0])

    @patch("main.verificar_autenticacao")
    @patch("main.db.collection")
    def test_obter_pedido_erro_interno(self, mock_db_collection, mock_verificar_autenticacao):
        """Testa se a função retorna erro interno do servidor quando ocorre uma exceção"""
        mock_verificar_autenticacao.return_value = ({"uid": "user123"}, None, 200)

        # Simula um erro inesperado ao acessar o Firestore
        mock_db_collection.side_effect = Exception("Erro inesperado")

        with self.app.test_request_context('/pedidos/123', method="GET"):
            response = obter_pedido(Request.from_values())
        
        self.assertEqual(response[1], 500)
        self.assertIn("Erro inesperado", response[0])

if __name__ == '__main__':
    unittest.main()
