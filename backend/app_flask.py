# Sistema de Gestão Escolar - Backend com Flask
# Flask + SQLAlchemy + SQLite

from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy.orm import Session
from datetime import date, datetime
import models
import database
import json

# Inicializar Flask
app = Flask(__name__)
CORS(app)  # Habilitar CORS para todas as rotas

# Criar tabelas no banco de dados
models.Base.metadata.create_all(bind=database.engine)

def get_db():
    """Função para obter sessão do banco de dados"""
    db = database.SessionLocal()
    try:
        return db
    finally:
        pass  # Não fechar aqui, fechar manualmente

# =====================================================
# ENDPOINTS DE SAÚDE
# =====================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de verificação de saúde da API"""
    return jsonify({
        "status": "healthy",
        "message": "Sistema de Gestão Escolar API está funcionando",
        "timestamp": datetime.now().isoformat()
    })

# =====================================================
# ENDPOINTS DE TURMAS
# =====================================================

@app.route('/turmas', methods=['GET'])
def get_turmas():
    """Listar todas as turmas"""
    db = get_db()
    try:
        turmas = db.query(models.Turma).all()
        result = []
        for turma in turmas:
            result.append({
                "id": turma.id,
                "nome": turma.nome,
                "capacidade": turma.capacidade
            })
        return jsonify(result)
    finally:
        db.close()

@app.route('/turmas', methods=['POST'])
def create_turma():
    """Criar nova turma"""
    db = get_db()
    try:
        data = request.get_json()
        
        # Verificar se já existe turma com o mesmo nome
        existing_turma = db.query(models.Turma).filter(
            models.Turma.nome == data['nome']
        ).first()
        
        if existing_turma:
            return jsonify({"detail": "Já existe uma turma com este nome"}), 400
        
        turma = models.Turma(
            nome=data['nome'],
            capacidade=data['capacidade']
        )
        db.add(turma)
        db.commit()
        db.refresh(turma)
        
        return jsonify({
            "id": turma.id,
            "nome": turma.nome,
            "capacidade": turma.capacidade
        }), 201
        
    except Exception as e:
        db.rollback()
        return jsonify({"detail": "Erro interno do servidor"}), 500
    finally:
        db.close()

@app.route('/turmas/<int:turma_id>', methods=['DELETE'])
def delete_turma(turma_id):
    """Excluir turma"""
    db = get_db()
    try:
        turma = db.query(models.Turma).filter(models.Turma.id == turma_id).first()
        
        if not turma:
            return jsonify({"detail": "Turma não encontrada"}), 404
        
        # Verificar se há alunos matriculados
        alunos_matriculados = db.query(models.Aluno).filter(
            models.Aluno.turma_id == turma_id
        ).count()
        
        if alunos_matriculados > 0:
            return jsonify({
                "detail": "Não é possível excluir turma com alunos matriculados"
            }), 400
        
        db.delete(turma)
        db.commit()
        
        return jsonify({"message": "Turma excluída com sucesso"})
        
    except Exception as e:
        db.rollback()
        return jsonify({"detail": "Erro interno do servidor"}), 500
    finally:
        db.close()

# =====================================================
# ENDPOINTS DE ALUNOS
# =====================================================

@app.route('/alunos', methods=['GET'])
def get_alunos():
    """Listar alunos com filtros opcionais"""
    db = get_db()
    try:
        query = db.query(models.Aluno)
        
        # Filtros opcionais
        search = request.args.get('search')
        turma_id = request.args.get('turma_id')
        status = request.args.get('status')
        
        if search:
            query = query.filter(models.Aluno.nome.ilike(f"%{search}%"))
        
        if turma_id:
            query = query.filter(models.Aluno.turma_id == int(turma_id))
        
        if status:
            query = query.filter(models.Aluno.status == status)
        
        alunos = query.all()
        
        # Adicionar nome da turma
        result = []
        for aluno in alunos:
            aluno_dict = {
                "id": aluno.id,
                "nome": aluno.nome,
                "data_nascimento": aluno.data_nascimento.isoformat(),
                "email": aluno.email,
                "status": aluno.status,
                "turma_id": aluno.turma_id,
                "turma_nome": None
            }
            
            if aluno.turma_id:
                turma = db.query(models.Turma).filter(models.Turma.id == aluno.turma_id).first()
                if turma:
                    aluno_dict["turma_nome"] = turma.nome
            
            result.append(aluno_dict)
        
        return jsonify(result)
        
    finally:
        db.close()

@app.route('/alunos', methods=['POST'])
def create_aluno():
    """Criar novo aluno"""
    db = get_db()
    try:
        data = request.get_json()
        
        # Converter string de data para objeto date
        data_nascimento = datetime.strptime(data['data_nascimento'], '%Y-%m-%d').date()
        
        # Verificar se a turma existe (se fornecida)
        if data.get('turma_id'):
            turma = db.query(models.Turma).filter(models.Turma.id == data['turma_id']).first()
            if not turma:
                return jsonify({"detail": "Turma não encontrada"}), 404
            
            # Verificar capacidade da turma
            alunos_na_turma = db.query(models.Aluno).filter(
                models.Aluno.turma_id == data['turma_id']
            ).count()
            
            if alunos_na_turma >= turma.capacidade:
                return jsonify({
                    "detail": "Turma já atingiu sua capacidade máxima"
                }), 400
        
        aluno = models.Aluno(
            nome=data['nome'],
            data_nascimento=data_nascimento,
            email=data.get('email'),
            status=data['status'],
            turma_id=data.get('turma_id')
        )
        
        db.add(aluno)
        db.commit()
        db.refresh(aluno)
        
        # Retornar com nome da turma
        result = {
            "id": aluno.id,
            "nome": aluno.nome,
            "data_nascimento": aluno.data_nascimento.isoformat(),
            "email": aluno.email,
            "status": aluno.status,
            "turma_id": aluno.turma_id,
            "turma_nome": None
        }
        
        if aluno.turma_id:
            turma = db.query(models.Turma).filter(models.Turma.id == aluno.turma_id).first()
            if turma:
                result["turma_nome"] = turma.nome
        
        return jsonify(result), 201
        
    except Exception as e:
        db.rollback()
        return jsonify({"detail": "Erro interno do servidor"}), 500
    finally:
        db.close()

@app.route('/alunos/<int:aluno_id>', methods=['DELETE'])
def delete_aluno(aluno_id):
    """Excluir aluno"""
    db = get_db()
    try:
        aluno = db.query(models.Aluno).filter(models.Aluno.id == aluno_id).first()
        
        if not aluno:
            return jsonify({"detail": "Aluno não encontrado"}), 404
        
        db.delete(aluno)
        db.commit()
        
        return jsonify({"message": "Aluno excluído com sucesso"})
        
    except Exception as e:
        db.rollback()
        return jsonify({"detail": "Erro interno do servidor"}), 500
    finally:
        db.close()

# =====================================================
# ENDPOINTS DE MATRÍCULAS
# =====================================================

@app.route('/matriculas', methods=['POST'])
def create_matricula():
    """Matricular aluno em uma turma"""
    db = get_db()
    try:
        data = request.get_json()
        
        # Verificar se o aluno existe
        aluno = db.query(models.Aluno).filter(models.Aluno.id == data['aluno_id']).first()
        if not aluno:
            return jsonify({"detail": "Aluno não encontrado"}), 404
        
        # Verificar se a turma existe
        turma = db.query(models.Turma).filter(models.Turma.id == data['turma_id']).first()
        if not turma:
            return jsonify({"detail": "Turma não encontrada"}), 404
        
        # Verificar se o aluno já está matriculado
        if aluno.turma_id:
            return jsonify({
                "detail": "Aluno já está matriculado em uma turma"
            }), 400
        
        # Verificar capacidade da turma
        alunos_na_turma = db.query(models.Aluno).filter(
            models.Aluno.turma_id == data['turma_id']
        ).count()
        
        if alunos_na_turma >= turma.capacidade:
            return jsonify({
                "detail": "Turma já atingiu sua capacidade máxima"
            }), 400
        
        # Atualizar aluno
        aluno.turma_id = data['turma_id']
        aluno.status = "ativo"
        
        db.commit()
        
        return jsonify({"message": "Aluno matriculado com sucesso"})
        
    except Exception as e:
        db.rollback()
        return jsonify({"detail": "Erro interno do servidor"}), 500
    finally:
        db.close()

# =====================================================
# ENDPOINTS DE ESTATÍSTICAS
# =====================================================

@app.route('/estatisticas', methods=['GET'])
def get_estatisticas():
    """Obter estatísticas gerais do sistema"""
    db = get_db()
    try:
        total_alunos = db.query(models.Aluno).count()
        alunos_ativos = db.query(models.Aluno).filter(models.Aluno.status == "ativo").count()
        total_turmas = db.query(models.Turma).count()
        
        return jsonify({
            "total_alunos": total_alunos,
            "alunos_ativos": alunos_ativos,
            "total_turmas": total_turmas
        })
        
    except Exception as e:
        return jsonify({"detail": "Erro interno do servidor"}), 500
    finally:
        db.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
