# Sistema de Gestão Escolar - Backend com Flask
# Flask + SQLAlchemy + SQLite + Autenticação

from flask import Flask, request, jsonify, session, send_from_directory
from flask_session import Session
from sqlalchemy.orm import Session as DBSession
from datetime import date, datetime
from functools import wraps
import models
import database
import json
import os

# Inicializar Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'escola-secret-key-2025'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'escola:'
app.config['SESSION_COOKIE_SECURE'] = False  # Para desenvolvimento HTTP
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Inicializar sessões
Session(app)

# Monkey patch para corrigir bug do Flask-Session/Python 3.13 (session_id como bytes)
import flask_session.sessions as flask_sessions
_orig_save_session = flask_sessions.FileSystemSessionInterface.save_session
def patched_save_session(self, app, session, response):
    # Garante que session.sid seja string
    if hasattr(session, 'sid') and isinstance(session.sid, bytes):
        session.sid = session.sid.decode('utf-8')
    # Garante que session_id passado para set_cookie seja string
    orig_set_cookie = response.set_cookie
    def safe_set_cookie(key, value, *args, **kwargs):
        if isinstance(value, bytes):
            value = value.decode('utf-8')
        return orig_set_cookie(key, value, *args, **kwargs)
    response.set_cookie = safe_set_cookie
    return _orig_save_session(self, app, session, response)
flask_sessions.FileSystemSessionInterface.save_session = patched_save_session

# Criar tabelas no banco de dados
models.Base.metadata.create_all(bind=database.engine)

# Adicionar headers CORS manualmente para garantir compatibilidade
@app.after_request
def after_request(response):
    origin = request.headers.get('Origin')
    if origin:
        response.headers.add('Access-Control-Allow-Origin', origin)
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    # Expor Set-Cookie para ferramentas de debug no navegador
    response.headers.add('Access-Control-Expose-Headers', 'Set-Cookie')
    return response

@app.before_request
def before_request():
    # Log simples para debug de CORS e sessão
    try:
        print(f"[REQ] {request.method} {request.path} | Origin={request.headers.get('Origin')} | Cookie={'session' in (request.headers.get('Cookie') or '')}")
    except Exception:
        pass
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-Requested-With')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

# =====================================================
# ERRO HANDLERS (RETORNAR JSON PARA ROTAS DE API)
# =====================================================

API_PREFIXES = (
    '/auth', '/alunos', '/turmas', '/matriculas', '/estatisticas', '/health', '/test-cors', '/debug'
)

def _is_api_path(path: str) -> bool:
    return any(path.startswith(p) for p in API_PREFIXES)

@app.errorhandler(404)
def handle_404(e):
    if _is_api_path(request.path):
        return jsonify({"detail": "Recurso não encontrado", "path": request.path}), 404
    # Para o frontend, retornar index.html (SPA)
    try:
        return send_from_directory(FRONTEND_DIR, 'index.html')
    except Exception:
        return jsonify({"detail": "Not Found"}), 404

@app.errorhandler(405)
def handle_405(e):
    if _is_api_path(request.path):
        return jsonify({"detail": "Método não permitido", "path": request.path}), 405
    return jsonify({"detail": "Método não permitido"}), 405

@app.errorhandler(500)
def handle_500(e):
    if _is_api_path(request.path):
        return jsonify({"detail": "Erro interno do servidor"}), 500
    return jsonify({"detail": "Erro interno do servidor"}), 500

# =====================================================
# SERVIR FRONTEND PELO MESMO HOST/PORTA (DESENVOLVIMENTO)
# =====================================================

FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_frontend(path):
    # Mapeia todos os caminhos não-API para arquivos do frontend
    api_prefixes = ('auth/', 'alunos', 'turmas', 'matriculas', 'estatisticas', 'health', 'test-cors', 'debug/')
    if path.startswith(api_prefixes):
        return jsonify({'detail': 'Not Found'}), 404
    target = path or 'index.html'
    try:
        return send_from_directory(FRONTEND_DIR, target)
    except Exception:
        # fallback para index.html (SPA)
        return send_from_directory(FRONTEND_DIR, 'index.html')

# =====================================================
# ENDPOINT DE DEBUG (DESENVOLVIMENTO)
# =====================================================

@app.route('/debug/session', methods=['GET'])
def debug_session():
    try:
        info = {
            'keys': list(session.keys()),
            'has_user_id': 'user_id' in session,
            'username': session.get('username'),
            'tipo': session.get('tipo')
        }
        return jsonify(info)
    except Exception:
        return jsonify({'error': 'debug failed'}), 500

def get_db():
    """Função para obter sessão do banco de dados"""
    db = database.SessionLocal()
    try:
        return db
    finally:
        pass  # Não fechar aqui, fechar manualmente

# =====================================================
# DECORADORES DE AUTENTICAÇÃO
# =====================================================

def login_required(f):
    """Decorator que exige que o usuário esteja logado"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"detail": "Acesso não autorizado. Faça login primeiro."}), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator que exige que o usuário seja administrador"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({"detail": "Acesso não autorizado. Faça login primeiro."}), 401
        
        db = get_db()
        try:
            user = db.query(models.Usuario).filter(models.Usuario.id == session['user_id']).first()
            if not user or user.tipo != 'admin':
                return jsonify({"detail": "Acesso negado. Apenas administradores podem realizar esta ação."}), 403
        finally:
            db.close()
        
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Retorna o usuário atual da sessão"""
    if 'user_id' not in session:
        return None
    
    db = get_db()
    try:
        user = db.query(models.Usuario).filter(models.Usuario.id == session['user_id']).first()
        return user
    finally:
        db.close()

# =====================================================
# ENDPOINTS DE AUTENTICAÇÃO
# =====================================================

@app.route('/auth/login', methods=['POST'])
def login():
    """Endpoint de login"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({"detail": "Username e password são obrigatórios"}), 400
        
        db = get_db()
        try:
            user = db.query(models.Usuario).filter(
                models.Usuario.username == username,
                models.Usuario.ativo == True
            ).first()
            
            if not user or not user.check_password(password):
                return jsonify({"detail": "Credenciais inválidas"}), 401
            
            # Atualizar último login
            user.ultimo_login = datetime.utcnow()
            db.commit()
            
            # Criar sessão
            session['user_id'] = user.id
            session['username'] = user.username
            session['tipo'] = user.tipo
            session['nome_completo'] = user.nome_completo
            
            return jsonify({
                "message": "Login realizado com sucesso",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "nome_completo": user.nome_completo,
                    "tipo": user.tipo,
                    "is_admin": user.is_admin
                }
            })
            
        finally:
            db.close()
            
    except Exception as e:
        import traceback
        print("[LOGIN ERROR]", e)
        traceback.print_exc()
        return jsonify({"detail": f"Erro interno do servidor: {str(e)}"}), 500

@app.route('/auth/logout', methods=['POST'])
@login_required
def logout():
    """Endpoint de logout"""
    session.clear()
    return jsonify({"message": "Logout realizado com sucesso"})

@app.route('/auth/me', methods=['GET'])
@login_required
def get_current_user_info():
    """Retorna informações do usuário atual"""
    user = get_current_user()
    if not user:
        return jsonify({"detail": "Usuário não encontrado"}), 404
    
    return jsonify({
        "id": user.id,
        "username": user.username,
        "nome_completo": user.nome_completo,
        "email": user.email,
        "tipo": user.tipo,
        "is_admin": user.is_admin,
        "ultimo_login": user.ultimo_login.isoformat() if user.ultimo_login else None
    })

@app.route('/auth/usuarios', methods=['GET'])
@admin_required
def get_usuarios():
    """Listar todos os usuários (apenas admin)"""
    db = get_db()
    try:
        usuarios = db.query(models.Usuario).all()
        result = []
        for usuario in usuarios:
            result.append({
                "id": usuario.id,
                "username": usuario.username,
                "nome_completo": usuario.nome_completo,
                "email": usuario.email,
                "tipo": usuario.tipo,
                "ativo": usuario.ativo,
                "ultimo_login": usuario.ultimo_login.isoformat() if usuario.ultimo_login else None
            })
        return jsonify(result)
    finally:
        db.close()

@app.route('/auth/usuarios', methods=['POST'])
@admin_required
def create_usuario():
    print('[USUARIO CREATE] Requisição recebida:', request.json)
    """Criar um novo usuário do tipo professor apenas com username e senha"""
    db = get_db()
    data = request.get_json() or {}
    username = (data.get('username') or '').strip()
    senha = data.get('senha') or ''
    if not username or not senha:
        return jsonify({'message': 'username e senha são obrigatórios.'}), 400
    # Verificar duplicidade
    if db.query(models.Usuario).filter(models.Usuario.username == username).first():
        return jsonify({'message': 'Já existe um usuário com este username.'}), 400
    # Criar usuário com nome_completo igual ao username e tipo professor
    usuario = models.Usuario(
        username=username,
        nome_completo=username,
        email=None,
        tipo='professor',
        ativo=True
    )
    usuario.set_password(senha)
    try:
        db.add(usuario)
        db.commit()
        user_id = usuario.id
        db.close()
        return jsonify({'message': 'Usuário (professor) criado com sucesso!', 'id': user_id}), 201
    except Exception as e:
        import traceback
        print('[USUARIO CREATE ERROR]', e)
        traceback.print_exc()
        db.rollback()
        db.close()
        return jsonify({'message': f'Erro ao criar usuário: {str(e)}'}), 500

# =====================================================
# ENDPOINTS DE SAÚDE
# =====================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de verificação de saúde da API"""
    return jsonify({
        "status": "healthy",
        "message": "Sistema de Gestão Escolar API está funcionando",
        "timestamp": datetime.now().isoformat(),
        "session_info": {
            "session_keys": list(session.keys()) if session else [],
            "has_user_id": 'user_id' in session if session else False
        }
    })

@app.route('/test-cors', methods=['GET', 'POST', 'OPTIONS'])
def test_cors():
    """Endpoint para testar configuração CORS"""
    if request.method == 'OPTIONS':
        return '', 200
    
    return jsonify({
        "message": "CORS funcionando",
        "method": request.method,
        "origin": request.headers.get('Origin', 'No origin'),
        "user_agent": request.headers.get('User-Agent', 'No user agent')
    })

# =====================================================
# ENDPOINTS DE TURMAS
# =====================================================

@app.route('/turmas', methods=['GET'])
@login_required
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
@admin_required
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
@admin_required
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
@login_required
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
@admin_required
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
@admin_required
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
@admin_required
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
@login_required
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
