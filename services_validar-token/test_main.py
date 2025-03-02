import unittest
import json
from unittest.mock import patch, MagicMock
from flask import Flask, Request
from main import validate_token

class TestValidateToken(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.client = self.app.test_client()

    def test_validate_token_opcoes(self):
        """Testa se a função responde corretamente a requisições OPTIONS"""
        with self.app.test_request_context('/validate-token', method="OPTIONS"):
            response = validate_token(Request.from_values())
        
        self.assertEqual(response[1], 204)

    @patch("main.verificar_autenticacao")
    def test_validate_token_sem_autenticacao(self, mock_verificar_autenticacao):
        """Testa se a função retorna erro quando o token não é fornecido"""
        mock_verificar_autenticacao.return_value = (None, json.dumps({"error": "Token de autenticação ausente ou inválido"}), 401)

        with self.app.test_request_context('/validate-token', method="POST"):
            response = validate_token(Request.from_values())
        
        self.assertEqual(response[1], 401)
        self.assertIn("Token de autenticação ausente ou inválido", response[0])

    @patch("main.verificar_autenticacao")
    def test_validate_token_sucesso(self, mock_verificar_autenticacao):
        """Testa se a função valida corretamente um token JWT válido"""
        mock_user_data = {"uid": "user123", "email": "teste@email.com"}
        mock_verificar_autenticacao.return_value = (mock_user_data, None, 200)

        with self.app.test_request_context('/validate-token', method="POST"):
            response = validate_token(Request.from_values())

        self.assertEqual(response[1], 200)
        self.assertIn("Token válido", response[0])
        self.assertIn("user123", response[0])

    @patch("main.verificar_autenticacao")
    def test_validate_token_invalido(self, mock_verificar_autenticacao):
        """Testa se a função retorna erro quando o token é inválido ou expirado"""
        mock_verificar_autenticacao.return_value = (None, json.dumps({"error": "Token inválido ou expirado"}), 401)

        with self.app.test_request_context('/validate-token', method="POST"):
            response = validate_token(Request.from_values())

        self.assertEqual(response[1], 401)
        self.assertIn("Token inválido ou expirado", response[0])

if __name__ == '__main__':
    unittest.main()
