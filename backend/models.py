# Models - SQLAlchemy ORM Models para o Sistema de Gestão Escolar

from sqlalchemy import Column, Integer, String, Date, ForeignKey, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import hashlib

Base = declarative_base()

class Usuario(Base):
    """Modelo da entidade Usuario para sistema de autenticação"""
    __tablename__ = "usuarios"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    nome_completo = Column(String(100), nullable=False)
    email = Column(String(100), nullable=True, unique=True, index=True)
    tipo = Column(String(20), nullable=False, default="professor", index=True)  # admin ou professor
    ativo = Column(Boolean, default=True, nullable=False)
    data_cadastro = Column(DateTime, default=datetime.utcnow)
    ultimo_login = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<Usuario(id={self.id}, username='{self.username}', tipo='{self.tipo}')>"
    
    def set_password(self, password):
        """Define a senha do usuário com hash"""
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    def check_password(self, password):
        """Verifica se a senha está correta"""
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()
    
    @property
    def is_admin(self):
        """Verifica se o usuário é administrador"""
        return self.tipo == "admin"
    
    @property
    def is_professor(self):
        """Verifica se o usuário é professor"""
        return self.tipo == "professor"

class Turma(Base):
    """Modelo da entidade Turma"""
    __tablename__ = "turmas"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(50), unique=True, nullable=False, index=True)
    capacidade = Column(Integer, nullable=False)
    
    # Relacionamento com alunos
    alunos = relationship("Aluno", back_populates="turma")
    
    def __repr__(self):
        return f"<Turma(id={self.id}, nome='{self.nome}', capacidade={self.capacidade})>"

class Aluno(Base):
    """Modelo da entidade Aluno"""
    __tablename__ = "alunos"
    
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(80), nullable=False, index=True)
    data_nascimento = Column(Date, nullable=False)
    email = Column(String(100), nullable=True, unique=True, index=True)
    status = Column(String(20), nullable=False, default="inativo", index=True)
    turma_id = Column(Integer, ForeignKey("turmas.id"), nullable=True)
    data_cadastro = Column(DateTime, default=datetime.utcnow)
    data_atualizacao = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamento com turma
    turma = relationship("Turma", back_populates="alunos")
    
    def __repr__(self):
        return f"<Aluno(id={self.id}, nome='{self.nome}', status='{self.status}')>"
    
    @property
    def idade(self):
        """Calcula a idade do aluno baseada na data de nascimento"""
        from datetime import date
        today = date.today()
        return today.year - self.data_nascimento.year - (
            (today.month, today.day) < (self.data_nascimento.month, self.data_nascimento.day)
        )
