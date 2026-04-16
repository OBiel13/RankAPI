from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="RankAPI")

# Banco de dados falso na memória
banco_usuarios = {}

# Modelo de dados para o Cadastro
class Usuario(BaseModel):
    nickname: str
    email: str
    senha: str
    score: int = 0

class LoginData(BaseModel):
    email: str
    senha: str

@app.post("/usuarios/", summary="Cadastrar novo jogador")
def criar_usuario(user: Usuario):
    if user.email in banco_usuarios:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    banco_usuarios[user.email] = user
    return {"mensagem": "Usuário criado com sucesso", "nickname": user.nickname}

@app.post("/login/", summary="Fazer login")
def login(dados: LoginData):
    user = banco_usuarios.get(dados.email)
    if not user or user.senha != dados.senha:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
    return {"mensagem": "Login bem-sucedido", "nickname": user.nickname}

@app.put("/score/{email}", summary="Atualizar pontuação")
def atualizar_score(email: str, novo_score: int):
    if email not in banco_usuarios:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Bloqueia números negativos
    if novo_score < 0:
        raise HTTPException(status_code=400, detail="A pontuação não pode ser negativa")
        
    # Só atualiza se o novo_score for MAIOR que o recorde atual do jogador
    recorde_atual = banco_usuarios[email].score
    if novo_score > recorde_atual:
        banco_usuarios[email].score = novo_score
        return {"mensagem": "Novo recorde alcançado!", "novo_score": novo_score}
    else:
        return {"mensagem": "A pontuação não superou o recorde atual.", "recorde_mantido": recorde_atual}

@app.get("/ranking/", summary="Listar o placar global")
def obter_ranking():
    usuarios_lista = list(banco_usuarios.values())
    # Bônus: Já devolve a lista ordenada do maior score pro menor, pronto pro placar do jogo!
    usuarios_ordenados = sorted(usuarios_lista, key=lambda x: x.score, reverse=True)
    return {"ranking": usuarios_ordenados}