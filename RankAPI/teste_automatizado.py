import requests

BASE_URL = "http://127.0.0.1:8000"

print("Iniciando bateria de testes automatizados...\n")

def test_cadastro_valido():
    url = f"{BASE_URL}/usuarios/"
    payload = {"nickname": "robo_tester", "email": "robo@teste.com", "senha": "abc"}
    response = requests.post(url, json=payload)
    
    assert response.status_code == 200, f"Falha: Esperado 200, recebido {response.status_code}"
    print("✅ Teste 1 (Cadastro): Passou! Status 200 recebido.")

def test_login_invalido():
    
    url = f"{BASE_URL}/login/?email=robo@teste.com&senha=errada"
    response = requests.post(url)
    
    assert response.status_code == 401, f"Falha: Esperado 401, recebido {response.status_code}"
    print("✅ Teste 2 (Login Inválido): Passou! O sistema bloqueou o acesso com status 401.")

try:
    test_cadastro_valido()
    test_login_invalido()
    print("\nTodos os testes automatizados passaram com sucesso!")
except AssertionError as erro:
    print(f"\n❌ Erro na automação: {erro}")