# Database - Configuração do SQLAlchemy e SQLite

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

# Configuração do banco de dados SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"

# Criar engine do SQLAlchemy
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},  # Necessário para SQLite
    echo=False  # Set to True for SQL query logging during development
)

# Criar SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class para os models
Base = declarative_base()

# Dependency para obter sessão do banco de dados
def get_db():
    """
    Dependency que fornece uma sessão do banco de dados
    e garante que ela seja fechada após o uso
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Função para inicializar o banco de dados
def init_db():
    """
    Inicializa o banco de dados criando todas as tabelas
    """
    import models
    models.Base.metadata.create_all(bind=engine)

# Função para verificar se o banco existe
def database_exists():
    """
    Verifica se o arquivo do banco de dados existe
    """
    return os.path.exists("app.db")

# Função para obter informações do banco
def get_database_info():
    """
    Retorna informações sobre o banco de dados
    """
    return {
        "database_url": SQLALCHEMY_DATABASE_URL,
        "database_exists": database_exists(),
        "engine_info": str(engine.url)
    }
