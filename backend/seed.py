# Seed Script - Populando o banco com dados de exemplo

import sys
import os
from datetime import date, timedelta
from sqlalchemy.orm import Session

# Adicionar o diretório backend ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, engine
import models

def create_seed_data():
    """
    Cria dados de exemplo para o sistema de gestão escolar
    """
    # Criar as tabelas se não existirem
    models.Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Verificar se já existem dados
        if db.query(models.Turma).count() > 0:
            print("⚠️  O banco de dados já contém dados. Executando limpeza...")
            # Limpar dados existentes
            db.query(models.Aluno).delete()
            db.query(models.Turma).delete()
            db.query(models.Usuario).delete()
            db.commit()
        
        print("👥 Criando usuários do sistema...")
        
        # Criar usuários
        usuarios_data = [
            {
                "username": "admin",
                "nome_completo": "Administrador do Sistema",
                "email": "admin@escola.com",
                "tipo": "admin",
                "password": "admin123"
            },
            {
                "username": "prof.maria",
                "nome_completo": "Maria Silva Santos",
                "email": "maria.santos@escola.com",
                "tipo": "professor",
                "password": "prof123"
            },
            {
                "username": "prof.joao",
                "nome_completo": "João Carlos Lima",
                "email": "joao.lima@escola.com",
                "tipo": "professor",
                "password": "prof123"
            },
            {
                "username": "prof.ana",
                "nome_completo": "Ana Paula Costa",
                "email": "ana.costa@escola.com",
                "tipo": "professor",
                "password": "prof123"
            }
        ]
        
        usuarios = []
        for user_data in usuarios_data:
            usuario = models.Usuario(
                username=user_data["username"],
                nome_completo=user_data["nome_completo"],
                email=user_data["email"],
                tipo=user_data["tipo"]
            )
            usuario.set_password(user_data["password"])
            db.add(usuario)
            usuarios.append(usuario)
        
        db.commit()
        print(f"✅ Criados {len(usuarios)} usuários")
        
        print("📚 Criando turmas...")
        
        # Criar turmas
        turmas_data = [
            {"nome": "1º Ano A", "capacidade": 25},
            {"nome": "1º Ano B", "capacidade": 25},
            {"nome": "2º Ano A", "capacidade": 30},
            {"nome": "2º Ano B", "capacidade": 30},
            {"nome": "3º Ano A", "capacidade": 28},
            {"nome": "3º Ano B", "capacidade": 28},
            {"nome": "4º Ano A", "capacidade": 20},
            {"nome": "5º Ano A", "capacidade": 22},
        ]
        
        turmas = []
        for turma_data in turmas_data:
            turma = models.Turma(**turma_data)
            db.add(turma)
            turmas.append(turma)
        
        db.commit()
        
        # Refresh para obter os IDs
        for turma in turmas:
            db.refresh(turma)
        
        print(f"✅ Criadas {len(turmas)} turmas")
        print("👥 Criando alunos...")
        
        # Criar alunos
        alunos_data = [
            {"nome": "Ana Silva Santos", "data_nascimento": date(2012, 3, 15), "email": "ana.silva@email.com", "status": "ativo", "turma_id": turmas[0].id},
            {"nome": "Bruno Costa Lima", "data_nascimento": date(2011, 7, 22), "email": "bruno.costa@email.com", "status": "ativo", "turma_id": turmas[0].id},
            {"nome": "Carla Oliveira Souza", "data_nascimento": date(2012, 1, 8), "email": "carla.oliveira@email.com", "status": "ativo", "turma_id": turmas[0].id},
            {"nome": "Diego Ferreira Alves", "data_nascimento": date(2011, 11, 30), "email": "diego.ferreira@email.com", "status": "ativo", "turma_id": turmas[1].id},
            {"nome": "Eduarda Martins Rocha", "data_nascimento": date(2012, 5, 12), "email": "eduarda.martins@email.com", "status": "ativo", "turma_id": turmas[1].id},
            {"nome": "Felipe Santos Dias", "data_nascimento": date(2011, 9, 5), "email": "felipe.santos@email.com", "status": "ativo", "turma_id": turmas[1].id},
            {"nome": "Gabriela Lima Pereira", "data_nascimento": date(2010, 12, 18), "email": "gabriela.lima@email.com", "status": "ativo", "turma_id": turmas[2].id},
            {"nome": "Henrique Alves Barbosa", "data_nascimento": date(2011, 2, 25), "email": "henrique.alves@email.com", "status": "ativo", "turma_id": turmas[2].id},
            {"nome": "Isabela Rodrigues Nunes", "data_nascimento": date(2010, 8, 14), "email": "isabela.rodrigues@email.com", "status": "ativo", "turma_id": turmas[2].id},
            {"nome": "João Pedro Silva", "data_nascimento": date(2011, 4, 3), "email": "joao.pedro@email.com", "status": "ativo", "turma_id": turmas[3].id},
            {"nome": "Karen Lopes Machado", "data_nascimento": date(2010, 10, 27), "email": "karen.lopes@email.com", "status": "ativo", "turma_id": turmas[3].id},
            {"nome": "Leonardo Costa Ribeiro", "data_nascimento": date(2011, 6, 9), "email": "leonardo.costa@email.com", "status": "ativo", "turma_id": turmas[3].id},
            {"nome": "Mariana Sousa Cruz", "data_nascimento": date(2009, 11, 21), "email": "mariana.sousa@email.com", "status": "ativo", "turma_id": turmas[4].id},
            {"nome": "Nicolas Fernandes Melo", "data_nascimento": date(2010, 1, 16), "email": "nicolas.fernandes@email.com", "status": "ativo", "turma_id": turmas[4].id},
            {"nome": "Olivia Santos Carvalho", "data_nascimento": date(2009, 7, 8), "email": "olivia.santos@email.com", "status": "ativo", "turma_id": turmas[4].id},
            {"nome": "Pedro Henrique Moura", "data_nascimento": date(2010, 3, 29), "email": "pedro.henrique@email.com", "status": "ativo", "turma_id": turmas[5].id},
            {"nome": "Quésia Araújo Mendes", "data_nascimento": date(2009, 9, 12), "email": "quesia.araujo@email.com", "status": "ativo", "turma_id": turmas[5].id},
            {"nome": "Rafael Gomes Teixeira", "data_nascimento": date(2010, 5, 24), "email": "rafael.gomes@email.com", "status": "ativo", "turma_id": turmas[5].id},
            {"nome": "Sofia Vieira Nascimento", "data_nascimento": date(2008, 12, 7), "email": "sofia.vieira@email.com", "status": "ativo", "turma_id": turmas[6].id},
            {"nome": "Thiago Cardoso Farias", "data_nascimento": date(2009, 4, 19), "email": "thiago.cardoso@email.com", "status": "ativo", "turma_id": turmas[6].id},
            {"nome": "Valentina Cruz Monteiro", "data_nascimento": date(2007, 8, 31), "email": "valentina.cruz@email.com", "status": "ativo", "turma_id": turmas[7].id},
            {"nome": "William Ramos Andrade", "data_nascimento": date(2008, 2, 13), "email": "william.ramos@email.com", "status": "ativo", "turma_id": turmas[7].id},
            
            # Alguns alunos sem turma (não matriculados)
            {"nome": "Xavier Silva Pinto", "data_nascimento": date(2012, 6, 20), "email": "xavier.silva@email.com", "status": "inativo", "turma_id": None},
            {"nome": "Yasmin Torres Batista", "data_nascimento": date(2011, 10, 4), "email": "yasmin.torres@email.com", "status": "inativo", "turma_id": None},
            {"nome": "Zacarias Almeida Costa", "data_nascimento": date(2013, 1, 28), "email": "zacarias.almeida@email.com", "status": "inativo", "turma_id": None},
        ]
        
        alunos = []
        for aluno_data in alunos_data:
            aluno = models.Aluno(**aluno_data)
            db.add(aluno)
            alunos.append(aluno)
        
        db.commit()
        
        print(f"✅ Criados {len(alunos)} alunos")
        
        # Estatísticas finais
        total_usuarios = db.query(models.Usuario).count()
        total_turmas = db.query(models.Turma).count()
        total_alunos = db.query(models.Aluno).count()
        alunos_ativos = db.query(models.Aluno).filter(models.Aluno.status == "ativo").count()
        
        print("\n📊 Resumo dos dados criados:")
        print(f"👥 Usuários: {total_usuarios}")
        print(f"🏫 Turmas: {total_turmas}")
        print(f"�‍🎓 Alunos: {total_alunos}")
        print(f"✅ Alunos Ativos: {alunos_ativos}")
        
        matriculados = sum(1 for aluno in alunos if aluno.turma_id is not None)
        nao_matriculados = len(alunos) - matriculados
        
        print(f"📚 Alunos matriculados: {matriculados}")
        print(f"❌ Alunos não matriculados: {nao_matriculados}")
        
        print("\n🔍 Distribuição por turma:")
        for turma in turmas:
            count = sum(1 for aluno in alunos if aluno.turma_id == turma.id)
            print(f"   📚 {turma.nome}: {count}/{turma.capacidade} alunos")
        
        print("\n🔑 Credenciais de acesso:")
        print("👑 Administrador:")
        print("   Username: admin")
        print("   Password: admin123")
        print("\n👨‍🏫 Professores:")
        print("   Username: prof.maria | Password: prof123")
        print("   Username: prof.joao  | Password: prof123")
        print("   Username: prof.ana   | Password: prof123")
        
        print("\n🎉 Dados de exemplo criados com sucesso!")
        print("💡 Use estes dados para testar o sistema.")
        
    except Exception as e:
        print(f"❌ Erro ao criar dados de exemplo: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def clear_database():
    """
    Limpa todos os dados do banco de dados
    """
    db = SessionLocal()
    try:
        print("🗑️  Limpando banco de dados...")
        db.query(models.Aluno).delete()
        db.query(models.Turma).delete()
        db.query(models.Usuario).delete()
        db.commit()
        print("✅ Banco de dados limpo com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao limpar banco de dados: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def show_database_stats():
    """
    Mostra estatísticas do banco de dados
    """
    db = SessionLocal()
    try:
        turmas_count = db.query(models.Turma).count()
        alunos_count = db.query(models.Aluno).count()
        alunos_ativos = db.query(models.Aluno).filter(models.Aluno.status == 'ativo').count()
        alunos_matriculados = db.query(models.Aluno).filter(models.Aluno.turma_id.isnot(None)).count()
        
        print("\n📊 Estatísticas do Banco de Dados:")
        print(f"   🏫 Total de turmas: {turmas_count}")
        print(f"   👥 Total de alunos: {alunos_count}")
        print(f"   ✅ Alunos ativos: {alunos_ativos}")
        print(f"   📚 Alunos matriculados: {alunos_matriculados}")
        
        if turmas_count > 0:
            print("\n📋 Detalhes por turma:")
            turmas = db.query(models.Turma).all()
            for turma in turmas:
                count = db.query(models.Aluno).filter(models.Aluno.turma_id == turma.id).count()
                print(f"   📚 {turma.nome}: {count}/{turma.capacidade} alunos")
        
    except Exception as e:
        print(f"❌ Erro ao obter estatísticas: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "create":
            print("🌱 Iniciando criação de dados de exemplo...")
            create_seed_data()
        elif command == "clear":
            print("🗑️  Iniciando limpeza do banco de dados...")
            clear_database()
        elif command == "stats":
            show_database_stats()
        else:
            print("❌ Comando inválido. Use: create, clear ou stats")
    else:
        print("📚 Sistema de Gestão Escolar - Seed Script")
        print("Uso:")
        print("  python seed.py create  - Criar dados de exemplo")
        print("  python seed.py clear   - Limpar banco de dados")
        print("  python seed.py stats   - Mostrar estatísticas")
