# Sistema de Gestão Escolar - Backend Simplificado
# FastAPI + SQLAlchemy + SQLite

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import models
import database
from database import get_db
from pydantic import BaseModel, validator
from datetime import date, datetime

# Inicializar FastAPI
app = FastAPI(
    title="Sistema de Gestão Escolar API",
    description="API para gerenciamento de alunos, turmas e matrículas",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Criar tabelas no banco de dados
models.Base.metadata.create_all(bind=database.engine)

# =====================================================
# SCHEMAS PYDANTIC SIMPLIFICADOS
# =====================================================

class TurmaBase(BaseModel):
    nome: str
    capacidade: int

class TurmaCreate(TurmaBase):
    pass

class TurmaResponse(TurmaBase):
    id: int
    
    class Config:
        orm_mode = True

class AlunoBase(BaseModel):
    nome: str
    data_nascimento: date
    email: Optional[str] = None
    status: str
    turma_id: Optional[int] = None

class AlunoCreate(AlunoBase):
    pass

class AlunoResponse(AlunoBase):
    id: int
    turma_nome: Optional[str] = None
    
    class Config:
        orm_mode = True

class MatriculaCreate(BaseModel):
    aluno_id: int
    turma_id: int

# =====================================================
# ENDPOINTS DE SAÚDE
# =====================================================

@app.get("/health")
async def health_check():
    """Endpoint de verificação de saúde da API"""
    return {
        "status": "healthy",
        "message": "Sistema de Gestão Escolar API está funcionando",
        "timestamp": datetime.now().isoformat()
    }

# =====================================================
# ENDPOINTS DE TURMAS
# =====================================================

@app.get("/turmas", response_model=List[TurmaResponse])
async def get_turmas(db: Session = Depends(get_db)):
    """Listar todas as turmas"""
    turmas = db.query(models.Turma).all()
    return turmas

@app.post("/turmas", response_model=TurmaResponse)
async def create_turma(turma: TurmaCreate, db: Session = Depends(get_db)):
    """Criar nova turma"""
    try:
        # Verificar se já existe turma com o mesmo nome
        existing_turma = db.query(models.Turma).filter(
            models.Turma.nome == turma.nome
        ).first()
        
        if existing_turma:
            raise HTTPException(
                status_code=400,
                detail="Já existe uma turma com este nome"
            )
        
        db_turma = models.Turma(**turma.dict())
        db.add(db_turma)
        db.commit()
        db.refresh(db_turma)
        
        return db_turma
        
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.delete("/turmas/{turma_id}")
async def delete_turma(turma_id: int, db: Session = Depends(get_db)):
    """Excluir turma"""
    try:
        db_turma = db.query(models.Turma).filter(models.Turma.id == turma_id).first()
        
        if not db_turma:
            raise HTTPException(status_code=404, detail="Turma não encontrada")
        
        # Verificar se há alunos matriculados
        alunos_matriculados = db.query(models.Aluno).filter(
            models.Aluno.turma_id == turma_id
        ).count()
        
        if alunos_matriculados > 0:
            raise HTTPException(
                status_code=400,
                detail="Não é possível excluir turma com alunos matriculados"
            )
        
        db.delete(db_turma)
        db.commit()
        
        return {"message": "Turma excluída com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

# =====================================================
# ENDPOINTS DE ALUNOS
# =====================================================

@app.get("/alunos", response_model=List[AlunoResponse])
async def get_alunos(
    search: Optional[str] = Query(None, description="Buscar por nome"),
    turma_id: Optional[int] = Query(None, description="Filtrar por turma"),
    status: Optional[str] = Query(None, description="Filtrar por status"),
    db: Session = Depends(get_db)
):
    """Listar alunos com filtros opcionais"""
    query = db.query(models.Aluno)
    
    # Filtro de busca por nome
    if search:
        query = query.filter(models.Aluno.nome.ilike(f"%{search}%"))
    
    # Filtro por turma
    if turma_id:
        query = query.filter(models.Aluno.turma_id == turma_id)
    
    # Filtro por status
    if status:
        query = query.filter(models.Aluno.status == status)
    
    alunos = query.all()
    
    # Adicionar nome da turma para cada aluno
    result = []
    for aluno in alunos:
        aluno_dict = {
            "id": aluno.id,
            "nome": aluno.nome,
            "data_nascimento": aluno.data_nascimento,
            "email": aluno.email,
            "status": aluno.status,
            "turma_id": aluno.turma_id,
            "turma_nome": None
        }
        
        if aluno.turma_id:
            turma = db.query(models.Turma).filter(models.Turma.id == aluno.turma_id).first()
            if turma:
                aluno_dict["turma_nome"] = turma.nome
        
        result.append(AlunoResponse(**aluno_dict))
    
    return result

@app.post("/alunos", response_model=AlunoResponse)
async def create_aluno(aluno: AlunoCreate, db: Session = Depends(get_db)):
    """Criar novo aluno"""
    try:
        # Verificar se a turma existe (se fornecida)
        if aluno.turma_id:
            turma = db.query(models.Turma).filter(models.Turma.id == aluno.turma_id).first()
            if not turma:
                raise HTTPException(status_code=404, detail="Turma não encontrada")
            
            # Verificar capacidade da turma
            alunos_na_turma = db.query(models.Aluno).filter(
                models.Aluno.turma_id == aluno.turma_id
            ).count()
            
            if alunos_na_turma >= turma.capacidade:
                raise HTTPException(
                    status_code=400,
                    detail="Turma já atingiu sua capacidade máxima"
                )
        
        db_aluno = models.Aluno(**aluno.dict())
        db.add(db_aluno)
        db.commit()
        db.refresh(db_aluno)
        
        # Retornar com nome da turma
        result = {
            "id": db_aluno.id,
            "nome": db_aluno.nome,
            "data_nascimento": db_aluno.data_nascimento,
            "email": db_aluno.email,
            "status": db_aluno.status,
            "turma_id": db_aluno.turma_id,
            "turma_nome": None
        }
        
        if db_aluno.turma_id:
            turma = db.query(models.Turma).filter(models.Turma.id == db_aluno.turma_id).first()
            if turma:
                result["turma_nome"] = turma.nome
        
        return AlunoResponse(**result)
        
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

@app.delete("/alunos/{aluno_id}")
async def delete_aluno(aluno_id: int, db: Session = Depends(get_db)):
    """Excluir aluno"""
    try:
        db_aluno = db.query(models.Aluno).filter(models.Aluno.id == aluno_id).first()
        
        if not db_aluno:
            raise HTTPException(status_code=404, detail="Aluno não encontrado")
        
        db.delete(db_aluno)
        db.commit()
        
        return {"message": "Aluno excluído com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

# =====================================================
# ENDPOINTS DE MATRÍCULAS
# =====================================================

@app.post("/matriculas")
async def create_matricula(matricula: MatriculaCreate, db: Session = Depends(get_db)):
    """Matricular aluno em uma turma"""
    try:
        # Verificar se o aluno existe
        aluno = db.query(models.Aluno).filter(models.Aluno.id == matricula.aluno_id).first()
        if not aluno:
            raise HTTPException(status_code=404, detail="Aluno não encontrado")
        
        # Verificar se a turma existe
        turma = db.query(models.Turma).filter(models.Turma.id == matricula.turma_id).first()
        if not turma:
            raise HTTPException(status_code=404, detail="Turma não encontrada")
        
        # Verificar se o aluno já está matriculado em alguma turma
        if aluno.turma_id:
            raise HTTPException(
                status_code=400,
                detail="Aluno já está matriculado em uma turma"
            )
        
        # Verificar capacidade da turma
        alunos_na_turma = db.query(models.Aluno).filter(
            models.Aluno.turma_id == matricula.turma_id
        ).count()
        
        if alunos_na_turma >= turma.capacidade:
            raise HTTPException(
                status_code=400,
                detail="Turma já atingiu sua capacidade máxima"
            )
        
        # Atualizar aluno
        aluno.turma_id = matricula.turma_id
        aluno.status = "ativo"  # Alterar status para ativo ao matricular
        
        db.commit()
        db.refresh(aluno)
        
        return {"message": "Aluno matriculado com sucesso"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

# =====================================================
# ENDPOINTS DE ESTATÍSTICAS
# =====================================================

@app.get("/estatisticas")
async def get_estatisticas(db: Session = Depends(get_db)):
    """Obter estatísticas gerais do sistema"""
    try:
        total_alunos = db.query(models.Aluno).count()
        alunos_ativos = db.query(models.Aluno).filter(models.Aluno.status == "ativo").count()
        alunos_inativos = db.query(models.Aluno).filter(models.Aluno.status == "inativo").count()
        total_turmas = db.query(models.Turma).count()
        
        # Estatísticas por turma
        turmas_stats = []
        turmas = db.query(models.Turma).all()
        
        for turma in turmas:
            alunos_na_turma = db.query(models.Aluno).filter(
                models.Aluno.turma_id == turma.id
            ).count()
            
            turmas_stats.append({
                "turma_id": turma.id,
                "turma_nome": turma.nome,
                "capacidade": turma.capacidade,
                "ocupacao": alunos_na_turma,
                "percentual_ocupacao": round((alunos_na_turma / turma.capacidade) * 100, 1) if turma.capacidade > 0 else 0
            })
        
        return {
            "total_alunos": total_alunos,
            "alunos_ativos": alunos_ativos,
            "alunos_inativos": alunos_inativos,
            "total_turmas": total_turmas,
            "turmas": turmas_stats
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro interno do servidor")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
