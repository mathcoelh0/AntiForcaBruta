import requests
import time

def test_brute_force():
    url = 'http://localhost:5000/login'
    credentials = {
        'username': 'admin',
        'password': 'wrong_password'
    }

    print("Iniciando teste de força bruta...")
    
    for i in range(10):
        response = requests.post(url, json=credentials)
        print(f"Tentativa {i+1}: Status {response.status_code}")
        
        try:
            print(f"Resposta: {response.json()}")
        except:
            print(f"Resposta: Limite de requisições excedido")
        
        time.sleep(1)

if __name__ == '__main__':
    test_brute_force()