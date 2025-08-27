# Sistema de Gestão Escolar

## 📚 Sobre o Projeto

Sistema web completo para gestão de alunos, turmas e matrículas escolares, desenvolvido como projeto acadêmico seguindo as especificações do curso de Sistemas Web.

### 🎯 Características Principais

- **Frontend**: HTML5, CSS3 (Flex/Grid), JavaScript ES6+ (sem frameworks)
- **Backend**: Python FastAPI + SQLAlchemy + SQLite
- **Identidade Visual**: Design responsivo com cores azul (#2563EB), verde (#10B981) e laranja (#F97316)
- **Acessibilidade**: Navegação por teclado, ARIA labels, alto contraste
- **Funcionalidades**: CRUD completo, filtros avançados, exportação de dados

## 🚀 Funcionalidades

### 👥 Gestão de Alunos
- Cadastro, edição e exclusão de alunos
- Validações de dados (nome, idade, email)
- Controle de status (ativo/inativo)
- Busca por nome

### 🏫 Gestão de Turmas
- Criação e gerenciamento de turmas
- Controle de capacidade e ocupação
- Visualização de estatísticas

### 📋 Sistema de Matrículas
- Matrícula de alunos em turmas
- Validação de capacidade
- Alteração automática de status

### 📊 Relatórios e Exportação
- Exportação em CSV e JSON
- Estatísticas em tempo real
- Filtros combinados

## 🔧 Tecnologias Utilizadas

### Frontend
- **HTML5**: Estrutura semântica e acessível
- **CSS3**: Flexbox, Grid, variáveis CSS, responsividade
- **JavaScript ES6+**: Fetch API, async/await, modules

### Backend
- **Python 3.8+**: Linguagem principal
- **FastAPI**: Framework web moderno e rápido
- **SQLAlchemy**: ORM para banco de dados
- **SQLite**: Banco de dados relacional
- **Pydantic**: Validação de dados e serialização

### Ferramentas de Desenvolvimento
- **VS Code**: Editor principal
- **GitHub Copilot**: Assistente de código IA
- **Git**: Controle de versão
- **Thunder Client**: Testes de API

## 📁 Estrutura do Projeto

```
projeto_3bm_pt2/
├── frontend/
│   ├── index.html          # Página principal
│   ├── styles.css          # Estilos CSS
│   └── scripts.js          # JavaScript
├── backend/
│   ├── app.py              # API FastAPI
│   ├── models.py           # Modelos SQLAlchemy
│   ├── database.py         # Configuração do banco
│   ├── seed.py             # Script de dados exemplo
│   └── requirements.txt    # Dependências Python
├── README.md               # Este arquivo
├── REPORT.md               # Relatório técnico
└── .github/
    └── copilot-instructions.md
```

## 🚀 Como Executar

### Pré-requisitos
- Python 3.8 ou superior
- Navegador web moderno
- Git (opcional)

### 1. Backend (API)

```bash
# Navegar para o diretório backend
cd backend

# Criar ambiente virtual (recomendado)
python -m venv venv

# Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt

# Criar dados de exemplo
python seed.py create

# Executar servidor
uvicorn app:app --reload
```

A API estará disponível em: http://localhost:8000

### 2. Frontend

```bash
# Navegar para o diretório frontend
cd frontend

# Abrir o arquivo index.html em um servidor local
# Opção 1: Python
python -m http.server 3000

# Opção 2: Node.js (se disponível)
npx serve -p 3000

# Opção 3: Live Server (VS Code Extension)
# Clique direito em index.html > "Open with Live Server"
```

O frontend estará disponível em: http://localhost:3000

### 3. Testando a API

Acesse a documentação interativa da API em:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📋 Endpoints da API

### Saúde
- `GET /health` - Verificação de saúde da API

### Turmas
- `GET /turmas` - Listar todas as turmas
- `POST /turmas` - Criar nova turma
- `PUT /turmas/{id}` - Atualizar turma
- `DELETE /turmas/{id}` - Excluir turma

### Alunos
- `GET /alunos` - Listar alunos (com filtros)
- `POST /alunos` - Criar novo aluno
- `PUT /alunos/{id}` - Atualizar aluno
- `DELETE /alunos/{id}` - Excluir aluno

### Matrículas
- `POST /matriculas` - Matricular aluno em turma

### Estatísticas
- `GET /estatisticas` - Obter estatísticas gerais

## 🎨 Identidade Visual

### Cores
- **Primária**: #2563EB (Azul) - Headers, botões principais
- **Secundária**: #10B981 (Verde) - Ações positivas, status ativo
- **Acento**: #F97316 (Laranja) - Destaques, botões de ação
- **Fundo**: #F1F5F9 (Cinza claro) - Background principal
- **Texto**: #0B1220 (Preto azulado) - Texto principal

### Tipografia
- **Fonte**: Inter (sans-serif)
- **Pesos**: 300, 400, 500, 600, 700

## ♿ Acessibilidade

### Recursos Implementados
- **Navegação por teclado**: Tab, Enter, Escape
- **ARIA labels**: Rótulos descritivos para leitores de tela
- **Foco visível**: Outline azul em elementos focados
- **Alto contraste**: Razão mínima 4.5:1
- **Anúncios para leitores de tela**: Feedback de ações
- **Trap focus**: Foco contido em modais

### Atalhos de Teclado
- `Alt + N`: Novo aluno (na aba alunos)
- `Alt + T`: Nova turma (na aba turmas)
- `Alt + 1/2/3`: Alternar entre abas
- `Escape`: Fechar modais

## 🔄 Peculiaridades Implementadas

1. **✅ Acessibilidade Real**: ARIA, foco, navegação por teclado
2. **✅ Validações Custom**: Frontend e backend com regras específicas
3. **✅ Filtro Avançado**: Múltiplos critérios sem recarregar
4. **✅ Ordenação Persistida**: localStorage mantém preferências
5. **✅ Export CSV/JSON**: Exportação dos dados atuais
6. **✅ Seed Script**: Dados plausíveis para demonstração
7. **✅ Tratamento de Erros**: Toasts visuais + HTTP codes
8. **✅ Validações Coerentes**: Espelhamento front/back

## 🧪 Testando o Sistema

### Dados de Exemplo
Execute `python seed.py create` para criar:
- 8 turmas com diferentes capacidades
- 25 alunos (22 matriculados, 3 não matriculados)
- Distribuição realística por turmas

### Cenários de Teste
1. **Cadastro de Aluno**: Teste validações de nome, idade, email
2. **Matrícula**: Teste limites de capacidade das turmas
3. **Filtros**: Combine busca por nome, turma e status
4. **Ordenação**: Ordene por nome, idade, turma
5. **Exportação**: Exporte dados em CSV/JSON
6. **Acessibilidade**: Navegue apenas com teclado

## 🚧 Limitações Conhecidas

- Não há autenticação/autorização implementada
- Histórico de matrículas não é mantido
- Não há backup automático do banco de dados
- Paginação não implementada (adequado para datasets pequenos)

## 🔮 Melhorias Futuras

- Sistema de autenticação e permissões
- Histórico de mudanças e auditoria
- Dashboard com gráficos interativos
- Sistema de notificações
- Backup automático
- API de importação de dados
- Tema escuro completo
- Versão mobile dedicada

## 📄 Licença

Este projeto foi desenvolvido para fins acadêmicos como parte do curso de Sistemas Web.

## 👨‍💻 Autor

Desenvolvido com 💙 seguindo as especificações do projeto acadêmico.

---

**Versão**: 1.0.0  
**Data**: Agosto 2025
