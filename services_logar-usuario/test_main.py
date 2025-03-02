import unittest
import json
from unittest.mock import patch, MagicMock
from flask import Flask, Request
from main import login_user

class TestLoginUser(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.client = self.app.test_client()

    def test_login_user_opcoes(self):
        """Testa se a função responde corretamente a requisições OPTIONS"""
        with self.app.test_request_context('/login', method="OPTIONS"):
            response = login_user(Request.from_values())
        
        self.assertEqual(response[1], 204)

    def test_login_user_dados_faltando(self):
        """Testa se a função retorna erro quando email ou senha não são fornecidos"""
        with self.app.test_request_context('/login', method="POST", json={}):
            response = login_user(Request.from_values())
        
        self.assertEqual(response[1], 400)
        self.assertIn("Email e senha são obrigatórios", response[0])

    @patch("main.auth.get_user_by_email")
    @patch("main.auth.create_custom_token")
    def test_login_user_sucesso(self, mock_create_custom_token, mock_get_user_by_email):
        """Testa se a função retorna um token JWT com sucesso"""
        mock_user = MagicMock()
        mock_user.uid = "user123"
        mock_get_user_by_email.return_value = mock_user
        mock_create_custom_token.return_value = b"fake_jwt_token"

        with self.app.test_request_context('/login', method="POST", json={"email": "teste@email.com", "password": "senha123"}):
            response = login_user(Request.from_values())

        self.assertEqual(response[1], 200)
        self.assertIn("token", response[0])
        self.assertIn("fake_jwt_token", response[0])

    @patch("main.auth.get_user_by_email")
    def test_login_user_usuario_nao_encontrado(self, mock_get_user_by_email):
        """Testa se a função retorna erro quando o usuário não é encontrado"""
        mock_get_user_by_email.side_effect = Exception("Usuário não encontrado")

        with self.app.test_request_context('/login', method="POST", json={"email": "teste@email.com", "password": "senha123"}):
            response = login_user(Request.from_values())

        self.assertEqual(response[1], 500)
        self.assertIn("Usuário não encontrado", response[0])

    @patch("main.auth.create_custom_token")
    def test_login_user_erro_geracao_token(self, mock_create_custom_token):
        """Testa se a função retorna erro ao gerar o token JWT"""
        mock_create_custom_token.side_effect = Exception("Erro ao gerar token")

        with self.app.test_request_context('/login', method="POST", json={"email": "teste@email.com", "password": "senha123"}):
            response = login_user(Request.from_values())

        self.assertEqual(response[1], 500)
        self.assertIn("Erro ao gerar token", response[0])

if __name__ == '__main__':
    unittest.main()
