# Models - SQLAlchemy ORM Models para o Sistema de Gestão Escolar

from sqlalchemy import Column, Integer, String, Date, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

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
