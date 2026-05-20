from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session
import bcrypt  # <-- Agora estamos usando o bcrypt puro!

# ==========================================
# CONFIGURAÇÕES DO BANCO DE DADOS (SQLite)
# ==========================================
SQLALCHEMY_DATABASE_URL = "sqlite:///./rankapi.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class UsuarioDB(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nickname = Column(String, unique=True)
    email = Column(String, unique=True, index=True)
    senha = Column(String) 
    score = Column(Integer, default=0)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="RankAPI Final")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==========================================
# MODELOS DE DADOS
# ==========================================
class Usuario(BaseModel):
    nickname: str
    email: str
    senha: str
    score: int = 0

class LoginData(BaseModel):
    email: str
    senha: str

# ==========================================
# ROTAS DA API
# ==========================================
@app.post("/usuarios/", summary="Cadastrar novo jogador")
def criar_usuario(user: Usuario, db: Session = Depends(get_db)):
    usuario_existente = db.query(UsuarioDB).filter(UsuarioDB.email == user.email).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    
    # Criptografando com bcrypt puro (Adeus erro de 72 bytes!)
    senha_bytes = user.senha.encode('utf-8')
    senha_hash = bcrypt.hashpw(senha_bytes, bcrypt.gensalt()).decode('utf-8')
    
    novo_usuario = UsuarioDB(nickname=user.nickname, email=user.email, senha=senha_hash, score=user.score)
    db.add(novo_usuario)
    db.commit()
    
    return {"mensagem": "Usuário criado com sucesso", "nickname": user.nickname}

@app.post("/login/", summary="Fazer login")
def login(dados: LoginData, db: Session = Depends(get_db)):
    user = db.query(UsuarioDB).filter(UsuarioDB.email == dados.email).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
        
    # Verificando a senha criptografada
    senha_digitada_bytes = dados.senha.encode('utf-8')
    senha_banco_bytes = user.senha.encode('utf-8')
    
    if not bcrypt.checkpw(senha_digitada_bytes, senha_banco_bytes):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")
        
    return {"mensagem": "Login bem-sucedido", "nickname": user.nickname}

@app.put("/score/{email}", summary="Atualizar pontuação")
def atualizar_score(email: str, novo_score: int, db: Session = Depends(get_db)):
    user = db.query(UsuarioDB).filter(UsuarioDB.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    if novo_score < 0:
        raise HTTPException(status_code=400, detail="A pontuação não pode ser negativa")
        
    if novo_score > user.score:
        user.score = novo_score
        db.commit()
        return {"mensagem": "Novo recorde alcançado!", "novo_score": novo_score}
    else:
        return {"mensagem": "A pontuação não superou o recorde atual.", "recorde_mantido": user.score}

@app.get("/ranking/", summary="Listar o placar global")
def obter_ranking(db: Session = Depends(get_db)):
    usuarios = db.query(UsuarioDB).order_by(UsuarioDB.score.desc()).all()
    ranking_formatado = [{"nickname": u.nickname, "score": u.score} for u in usuarios]
    return {"ranking": ranking_formatado}