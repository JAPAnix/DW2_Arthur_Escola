// =====================================================
// SISTEMA DE GESTÃO ESCOLAR - SCRIPTS.JS
// Frontend JavaScript ES6+ sem frameworks
// =====================================================

// Configuração da API
const API_BASE_URL = 'http://localhost:8000';

// Estado da aplicação
let currentTab = 'alunos';
let currentSort = 'nome';
let sortOrder = 'asc';
let filters = {
    search: '',
    turma: '',
    status: ''
};

// Cache de dados
let alunosData = [];
let turmasData = [];

// =====================================================
// INICIALIZAÇÃO
// =====================================================

document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    loadInitialData();
});

function initializeApp() {
    // Configurar ordenação persistida
    const savedSort = localStorage.getItem('gestaoEscolar_sort');
    if (savedSort) {
        const sortData = JSON.parse(savedSort);
        currentSort = sortData.field;
        sortOrder = sortData.order;
        updateSortUI();
    }
    
    // Configurar tema (se implementado)
    const savedTheme = localStorage.getItem('gestaoEscolar_theme');
    if (savedTheme) {
        document.body.classList.toggle('dark-theme', savedTheme === 'dark');
    }
}

function setupEventListeners() {
    // Tabs
    document.getElementById('tabAlunos').addEventListener('click', () => switchTab('alunos'));
    document.getElementById('tabTurmas').addEventListener('click', () => switchTab('turmas'));
    document.getElementById('tabRelatorios').addEventListener('click', () => switchTab('relatorios'));
    
    // Busca
    const searchInput = document.getElementById('searchInput');
    const searchBtn = document.getElementById('searchBtn');
    
    searchInput.addEventListener('input', debounce(handleSearch, 300));
    searchBtn.addEventListener('click', handleSearch);
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSearch();
    });
    
    // Filtros
    document.getElementById('turmaFilter').addEventListener('change', handleFilterChange);
    document.getElementById('statusFilter').addEventListener('change', handleFilterChange);
    document.getElementById('clearFilters').addEventListener('click', clearFilters);
    
    // Ordenação
    document.getElementById('sortBy').addEventListener('change', handleSortChange);
    document.getElementById('sortOrder').addEventListener('click', toggleSortOrder);
    
    // Botões principais
    document.getElementById('btnNovoAluno').addEventListener('click', () => openModal('modalNovoAluno'));
    document.getElementById('btnNovaTurma').addEventListener('click', () => openModal('modalNovaTurma'));
    document.getElementById('btnExportar').addEventListener('click', handleExport);
    
    // Modais
    setupModalEventListeners();
    
    // Exportação
    setupExportEventListeners();
    
    // Teclas de atalho para acessibilidade
    document.addEventListener('keydown', handleKeyboardShortcuts);
}

function setupModalEventListeners() {
    // Modal Aluno
    const modalAluno = document.getElementById('modalNovoAluno');
    const formAluno = document.getElementById('formAluno');
    const cancelarAluno = document.getElementById('cancelarAluno');
    
    formAluno.addEventListener('submit', handleAlunoSubmit);
    cancelarAluno.addEventListener('click', () => closeModal('modalNovoAluno'));
    
    // Modal Turma
    const modalTurma = document.getElementById('modalNovaTurma');
    const formTurma = document.getElementById('formTurma');
    const cancelarTurma = document.getElementById('cancelarTurma');
    
    formTurma.addEventListener('submit', handleTurmaSubmit);
    cancelarTurma.addEventListener('click', () => closeModal('modalNovaTurma'));
    
    // Fechar modais clicando fora ou no X
    document.querySelectorAll('.modal').forEach(modal => {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) closeModal(modal.id);
        });
        
        const closeBtn = modal.querySelector('.modal-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => closeModal(modal.id));
        }
    });
    
    // ESC para fechar modais
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            const activeModal = document.querySelector('.modal.active');
            if (activeModal) closeModal(activeModal.id);
        }
    });
}

function setupExportEventListeners() {
    document.getElementById('exportAlunosCSV').addEventListener('click', () => exportData('alunos', 'csv'));
    document.getElementById('exportAlunosJSON').addEventListener('click', () => exportData('alunos', 'json'));
    document.getElementById('exportMatriculasCSV').addEventListener('click', () => exportData('matriculas', 'csv'));
    document.getElementById('exportMatriculasJSON').addEventListener('click', () => exportData('matriculas', 'json'));
}

// =====================================================
// NAVEGAÇÃO E TABS
// =====================================================

function switchTab(tabName) {
    // Atualizar estado
    currentTab = tabName;
    
    // Atualizar UI das tabs
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
        btn.setAttribute('aria-selected', 'false');
    });
    
    document.getElementById(`tab${capitalize(tabName)}`).classList.add('active');
    document.getElementById(`tab${capitalize(tabName)}`).setAttribute('aria-selected', 'true');
    
    // Mostrar seção correspondente
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
    });
    
    document.getElementById(`${tabName}Section`).classList.add('active');
    
    // Carregar dados específicos se necessário
    if (tabName === 'turmas' && turmasData.length === 0) {
        loadTurmas();
    }
    
    // Foco para acessibilidade
    const activeSection = document.getElementById(`${tabName}Section`);
    activeSection.focus();
}

// =====================================================
// CARREGAMENTO DE DADOS
// =====================================================

async function loadInitialData() {
    try {
        showLoading(true);
        await Promise.all([loadAlunos(), loadTurmas()]);
        updateStatistics();
        populateTurmaSelects();
    } catch (error) {
        showToast('Erro ao carregar dados iniciais', 'error');
        console.error('Erro ao carregar dados:', error);
    } finally {
        showLoading(false);
    }
}

async function loadAlunos() {
    try {
        const queryParams = new URLSearchParams();
        if (filters.search) queryParams.append('search', filters.search);
        if (filters.turma) queryParams.append('turma_id', filters.turma);
        if (filters.status) queryParams.append('status', filters.status);
        
        const response = await fetch(`${API_BASE_URL}/alunos?${queryParams}`);
        
        if (!response.ok) {
            throw new Error(`Erro ${response.status}: ${response.statusText}`);
        }
        
        alunosData = await response.json();
        renderAlunos();
        updateStatistics();
        
        // Anunciar mudança para leitores de tela
        announceToScreenReader(`${alunosData.length} alunos carregados`);
        
    } catch (error) {
        showToast('Erro ao carregar alunos', 'error');
        console.error('Erro ao carregar alunos:', error);
    }
}

async function loadTurmas() {
    try {
        const response = await fetch(`${API_BASE_URL}/turmas`);
        
        if (!response.ok) {
            throw new Error(`Erro ${response.status}: ${response.statusText}`);
        }
        
        turmasData = await response.json();
        renderTurmas();
        populateTurmaSelects();
        
    } catch (error) {
        showToast('Erro ao carregar turmas', 'error');
        console.error('Erro ao carregar turmas:', error);
    }
}

// =====================================================
// RENDERIZAÇÃO DE DADOS
// =====================================================

function renderAlunos() {
    const tbody = document.getElementById('alunosTableBody');
    
    if (alunosData.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="empty-state">
                    <h3>Nenhum aluno encontrado</h3>
                    <p>Adicione um novo aluno ou ajuste os filtros de busca</p>
                </td>
            </tr>
        `;
        return;
    }
    
    // Aplicar ordenação
    const sortedData = [...alunosData].sort((a, b) => {
        let valueA, valueB;
        
        switch (currentSort) {
            case 'nome':
                valueA = a.nome.toLowerCase();
                valueB = b.nome.toLowerCase();
                break;
            case 'idade':
                valueA = calculateAge(a.data_nascimento);
                valueB = calculateAge(b.data_nascimento);
                break;
            case 'turma':
                valueA = a.turma_nome || '';
                valueB = b.turma_nome || '';
                break;
            case 'status':
                valueA = a.status;
                valueB = b.status;
                break;
            default:
                valueA = a[currentSort] || '';
                valueB = b[currentSort] || '';
        }
        
        if (sortOrder === 'asc') {
            return valueA > valueB ? 1 : -1;
        } else {
            return valueA < valueB ? 1 : -1;
        }
    });
    
    tbody.innerHTML = sortedData.map(aluno => `
        <tr>
            <td>${escapeHtml(aluno.nome)}</td>
            <td>${formatDate(aluno.data_nascimento)} (${calculateAge(aluno.data_nascimento)} anos)</td>
            <td>${aluno.email ? escapeHtml(aluno.email) : '-'}</td>
            <td><span class="status-badge status-${aluno.status}">${aluno.status}</span></td>
            <td>${aluno.turma_nome ? escapeHtml(aluno.turma_nome) : '-'}</td>
            <td>
                <div class="action-btns">
                    <button class="btn-action btn-edit" onclick="editAluno(${aluno.id})" aria-label="Editar aluno ${escapeHtml(aluno.nome)}">
                        Editar
                    </button>
                    <button class="btn-action btn-delete" onclick="deleteAluno(${aluno.id})" aria-label="Excluir aluno ${escapeHtml(aluno.nome)}">
                        Excluir
                    </button>
                    ${!aluno.turma_id ? `
                        <button class="btn-action btn-matricular" onclick="openMatriculaModal(${aluno.id})" aria-label="Matricular aluno ${escapeHtml(aluno.nome)}">
                            Matricular
                        </button>
                    ` : ''}
                </div>
            </td>
        </tr>
    `).join('');
}

function renderTurmas() {
    const tbody = document.getElementById('turmasTableBody');
    
    if (turmasData.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="4" class="empty-state">
                    <h3>Nenhuma turma encontrada</h3>
                    <p>Cadastre a primeira turma para começar</p>
                </td>
            </tr>
        `;
        return;
    }
    
    tbody.innerHTML = turmasData.map(turma => {
        const ocupacao = alunosData.filter(aluno => aluno.turma_id === turma.id).length;
        const percentualOcupacao = (ocupacao / turma.capacidade * 100).toFixed(1);
        
        return `
            <tr>
                <td>${escapeHtml(turma.nome)}</td>
                <td>${turma.capacidade}</td>
                <td>
                    ${ocupacao}/${turma.capacidade} (${percentualOcupacao}%)
                    <div class="progress-bar" style="width: 100%; height: 4px; background: #E5E7EB; border-radius: 2px; margin-top: 4px;">
                        <div style="width: ${percentualOcupacao}%; height: 100%; background: ${ocupacao >= turma.capacidade ? '#EF4444' : '#10B981'}; border-radius: 2px;"></div>
                    </div>
                </td>
                <td>
                    <div class="action-btns">
                        <button class="btn-action btn-edit" onclick="editTurma(${turma.id})" aria-label="Editar turma ${escapeHtml(turma.nome)}">
                            Editar
                        </button>
                        <button class="btn-action btn-delete" onclick="deleteTurma(${turma.id})" aria-label="Excluir turma ${escapeHtml(turma.nome)}">
                            Excluir
                        </button>
                    </div>
                </td>
            </tr>
        `;
    }).join('');
}

// =====================================================
// BUSCA E FILTROS
// =====================================================

function handleSearch() {
    filters.search = document.getElementById('searchInput').value.trim();
    loadAlunos();
}

function handleFilterChange() {
    filters.turma = document.getElementById('turmaFilter').value;
    filters.status = document.getElementById('statusFilter').value;
    loadAlunos();
}

function clearFilters() {
    filters = { search: '', turma: '', status: '' };
    
    document.getElementById('searchInput').value = '';
    document.getElementById('turmaFilter').value = '';
    document.getElementById('statusFilter').value = '';
    
    loadAlunos();
    showToast('Filtros limpos');
}

// =====================================================
// ORDENAÇÃO
// =====================================================

function handleSortChange() {
    currentSort = document.getElementById('sortBy').value;
    saveSortPreference();
    renderAlunos();
}

function toggleSortOrder() {
    sortOrder = sortOrder === 'asc' ? 'desc' : 'asc';
    updateSortUI();
    saveSortPreference();
    renderAlunos();
}

function updateSortUI() {
    const sortBtn = document.getElementById('sortOrder');
    sortBtn.textContent = sortOrder === 'asc' ? '↑' : '↓';
    sortBtn.setAttribute('aria-label', `Ordem ${sortOrder === 'asc' ? 'crescente' : 'decrescente'}`);
    
    document.getElementById('sortBy').value = currentSort;
}

function saveSortPreference() {
    localStorage.setItem('gestaoEscolar_sort', JSON.stringify({
        field: currentSort,
        order: sortOrder
    }));
}

// =====================================================
// CRUD DE ALUNOS
// =====================================================

async function handleAlunoSubmit(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const alunoData = Object.fromEntries(formData);
    
    // Validações do frontend
    const validationError = validateAlunoData(alunoData);
    if (validationError) {
        showToast(validationError, 'error');
        return;
    }
    
    try {
        showLoading(true);
        
        const response = await fetch(`${API_BASE_URL}/alunos`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(alunoData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `Erro ${response.status}`);
        }
        
        await response.json();
        
        closeModal('modalNovoAluno');
        resetForm('formAluno');
        await loadAlunos();
        
        showToast('Aluno cadastrado com sucesso!');
        
    } catch (error) {
        showToast(`Erro ao cadastrar aluno: ${error.message}`, 'error');
        console.error('Erro ao cadastrar aluno:', error);
    } finally {
        showLoading(false);
    }
}

async function editAluno(id) {
    const aluno = alunosData.find(a => a.id === id);
    if (!aluno) return;
    
    // Preencher formulário com dados do aluno
    document.getElementById('nomeAluno').value = aluno.nome;
    document.getElementById('dataNascimento').value = aluno.data_nascimento;
    document.getElementById('emailAluno').value = aluno.email || '';
    document.getElementById('statusAluno').value = aluno.status;
    document.getElementById('turmaAluno').value = aluno.turma_id || '';
    
    // Alterar título do modal e adicionar ID para edição
    document.getElementById('modalTitleAluno').textContent = 'Editar Aluno';
    document.getElementById('formAluno').dataset.editId = id;
    
    openModal('modalNovoAluno');
}

async function deleteAluno(id) {
    const aluno = alunosData.find(a => a.id === id);
    if (!aluno) return;
    
    if (!confirm(`Tem certeza que deseja excluir o aluno "${aluno.nome}"?`)) {
        return;
    }
    
    try {
        showLoading(true);
        
        const response = await fetch(`${API_BASE_URL}/alunos/${id}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `Erro ${response.status}`);
        }
        
        await loadAlunos();
        showToast('Aluno excluído com sucesso!');
        
    } catch (error) {
        showToast(`Erro ao excluir aluno: ${error.message}`, 'error');
        console.error('Erro ao excluir aluno:', error);
    } finally {
        showLoading(false);
    }
}

// =====================================================
// CRUD DE TURMAS
// =====================================================

async function handleTurmaSubmit(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const turmaData = Object.fromEntries(formData);
    
    try {
        showLoading(true);
        
        const response = await fetch(`${API_BASE_URL}/turmas`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(turmaData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `Erro ${response.status}`);
        }
        
        await response.json();
        
        closeModal('modalNovaTurma');
        resetForm('formTurma');
        await loadTurmas();
        populateTurmaSelects();
        
        showToast('Turma cadastrada com sucesso!');
        
    } catch (error) {
        showToast(`Erro ao cadastrar turma: ${error.message}`, 'error');
        console.error('Erro ao cadastrar turma:', error);
    } finally {
        showLoading(false);
    }
}

async function editTurma(id) {
    const turma = turmasData.find(t => t.id === id);
    if (!turma) return;
    
    // Preencher formulário com dados da turma
    document.getElementById('nomeTurma').value = turma.nome;
    document.getElementById('capacidadeTurma').value = turma.capacidade;
    
    // Alterar título do modal e adicionar ID para edição
    document.getElementById('modalTitleTurma').textContent = 'Editar Turma';
    document.getElementById('formTurma').dataset.editId = id;
    
    openModal('modalNovaTurma');
}

async function deleteTurma(id) {
    const turma = turmasData.find(t => t.id === id);
    if (!turma) return;
    
    // Verificar se há alunos matriculados
    const alunosMatriculados = alunosData.filter(aluno => aluno.turma_id === id).length;
    if (alunosMatriculados > 0) {
        showToast('Não é possível excluir turma com alunos matriculados', 'error');
        return;
    }
    
    if (!confirm(`Tem certeza que deseja excluir a turma "${turma.nome}"?`)) {
        return;
    }
    
    try {
        showLoading(true);
        
        const response = await fetch(`${API_BASE_URL}/turmas/${id}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `Erro ${response.status}`);
        }
        
        await loadTurmas();
        populateTurmaSelects();
        showToast('Turma excluída com sucesso!');
        
    } catch (error) {
        showToast(`Erro ao excluir turma: ${error.message}`, 'error');
        console.error('Erro ao excluir turma:', error);
    } finally {
        showLoading(false);
    }
}

// =====================================================
// MATRÍCULAS
// =====================================================

async function openMatriculaModal(alunoId) {
    const aluno = alunosData.find(a => a.id === alunoId);
    if (!aluno || aluno.turma_id) return;
    
    // Criar modal dinâmico para matrícula
    const modal = document.createElement('div');
    modal.className = 'modal active';
    modal.id = 'modalMatricula';
    modal.innerHTML = `
        <div class="modal-content">
            <div class="modal-header">
                <h2>Matricular Aluno: ${escapeHtml(aluno.nome)}</h2>
                <button class="modal-close" aria-label="Fechar modal">&times;</button>
            </div>
            <form id="formMatricula" class="modal-body">
                <input type="hidden" name="aluno_id" value="${alunoId}">
                <div class="form-group">
                    <label for="turmaMatricula">Selecione a Turma *</label>
                    <select id="turmaMatricula" name="turma_id" required>
                        <option value="">Selecione uma turma</option>
                        ${turmasData.map(turma => {
                            const ocupacao = alunosData.filter(a => a.turma_id === turma.id).length;
                            const disponivel = ocupacao < turma.capacidade;
                            return `<option value="${turma.id}" ${!disponivel ? 'disabled' : ''}>
                                ${escapeHtml(turma.nome)} (${ocupacao}/${turma.capacidade})
                                ${!disponivel ? ' - LOTADA' : ''}
                            </option>`;
                        }).join('')}
                    </select>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn-secondary" onclick="closeMatriculaModal()">Cancelar</button>
                    <button type="submit" class="btn-primary">Matricular</button>
                </div>
            </form>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Event listeners
    modal.querySelector('.modal-close').addEventListener('click', closeMatriculaModal);
    modal.querySelector('#formMatricula').addEventListener('submit', handleMatriculaSubmit);
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeMatriculaModal();
    });
    
    // Foco para acessibilidade
    modal.querySelector('#turmaMatricula').focus();
}

function closeMatriculaModal() {
    const modal = document.getElementById('modalMatricula');
    if (modal) {
        modal.remove();
    }
}

async function handleMatriculaSubmit(e) {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    const matriculaData = Object.fromEntries(formData);
    
    try {
        showLoading(true);
        
        const response = await fetch(`${API_BASE_URL}/matriculas`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(matriculaData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `Erro ${response.status}`);
        }
        
        await response.json();
        
        closeMatriculaModal();
        await loadAlunos();
        
        showToast('Aluno matriculado com sucesso!');
        
    } catch (error) {
        showToast(`Erro ao matricular aluno: ${error.message}`, 'error');
        console.error('Erro ao matricular aluno:', error);
    } finally {
        showLoading(false);
    }
}

// =====================================================
// EXPORTAÇÃO DE DADOS
// =====================================================

async function exportData(type, format) {
    try {
        let data;
        let filename;
        
        if (type === 'alunos') {
            data = alunosData;
            filename = `alunos_${new Date().toISOString().split('T')[0]}`;
        } else if (type === 'matriculas') {
            data = alunosData.filter(aluno => aluno.turma_id);
            filename = `matriculas_${new Date().toISOString().split('T')[0]}`;
        }
        
        if (format === 'csv') {
            exportToCSV(data, filename, type);
        } else if (format === 'json') {
            exportToJSON(data, filename);
        }
        
        showToast(`Dados exportados em ${format.toUpperCase()}`);
        
    } catch (error) {
        showToast(`Erro ao exportar dados: ${error.message}`, 'error');
        console.error('Erro ao exportar:', error);
    }
}

function exportToCSV(data, filename, type) {
    let headers;
    let rows;
    
    if (type === 'alunos') {
        headers = ['ID', 'Nome', 'Data de Nascimento', 'Email', 'Status', 'Turma'];
        rows = data.map(aluno => [
            aluno.id,
            aluno.nome,
            aluno.data_nascimento,
            aluno.email || '',
            aluno.status,
            aluno.turma_nome || ''
        ]);
    } else {
        headers = ['Aluno ID', 'Nome do Aluno', 'Turma ID', 'Nome da Turma', 'Data de Matricula'];
        rows = data.map(aluno => [
            aluno.id,
            aluno.nome,
            aluno.turma_id,
            aluno.turma_nome,
            new Date().toISOString().split('T')[0] // Simplified
        ]);
    }
    
    const csvContent = [headers, ...rows]
        .map(row => row.map(field => `"${field}"`).join(','))
        .join('\n');
    
    downloadFile(csvContent, `${filename}.csv`, 'text/csv');
}

function exportToJSON(data, filename) {
    const jsonContent = JSON.stringify(data, null, 2);
    downloadFile(jsonContent, `${filename}.json`, 'application/json');
}

function downloadFile(content, filename, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.style.display = 'none';
    
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    
    URL.revokeObjectURL(url);
}

// =====================================================
// UTILITÁRIOS
// =====================================================

function openModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.classList.add('active');
    modal.setAttribute('aria-hidden', 'false');
    
    // Foco para acessibilidade
    const firstInput = modal.querySelector('input, select, textarea');
    if (firstInput) {
        setTimeout(() => firstInput.focus(), 100);
    }
    
    // Trap focus
    trapFocus(modal);
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.classList.remove('active');
    modal.setAttribute('aria-hidden', 'true');
    
    // Resetar formulário e estado
    const form = modal.querySelector('form');
    if (form) {
        resetForm(form.id);
        delete form.dataset.editId;
    }
    
    // Restaurar títulos originais
    if (modalId === 'modalNovoAluno') {
        document.getElementById('modalTitleAluno').textContent = 'Cadastrar Novo Aluno';
    } else if (modalId === 'modalNovaTurma') {
        document.getElementById('modalTitleTurma').textContent = 'Cadastrar Nova Turma';
    }
}

function resetForm(formId) {
    const form = document.getElementById(formId);
    form.reset();
    
    // Limpar mensagens de erro
    form.querySelectorAll('.error-message').forEach(msg => {
        msg.textContent = '';
    });
}

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type}`;
    toast.classList.add('show');
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

function showLoading(show) {
    document.body.classList.toggle('loading', show);
}

function updateStatistics() {
    document.getElementById('totalAlunos').textContent = alunosData.length;
    document.getElementById('alunosAtivos').textContent = alunosData.filter(a => a.status === 'ativo').length;
    document.getElementById('totalTurmas').textContent = turmasData.length;
}

function populateTurmaSelects() {
    const selects = ['turmaFilter', 'turmaAluno'];
    
    selects.forEach(selectId => {
        const select = document.getElementById(selectId);
        if (!select) return;
        
        // Preservar opção vazia
        const emptyOption = select.querySelector('option[value=""]');
        select.innerHTML = '';
        if (emptyOption) select.appendChild(emptyOption);
        
        // Adicionar turmas
        turmasData.forEach(turma => {
            const option = document.createElement('option');
            option.value = turma.id;
            option.textContent = turma.nome;
            select.appendChild(option);
        });
    });
}

function validateAlunoData(data) {
    // Validação de nome
    if (!data.nome || data.nome.length < 3 || data.nome.length > 80) {
        return 'Nome deve ter entre 3 e 80 caracteres';
    }
    
    // Validação de data de nascimento
    if (!data.data_nascimento) {
        return 'Data de nascimento é obrigatória';
    }
    
    const birthDate = new Date(data.data_nascimento);
    const minDate = new Date();
    minDate.setFullYear(minDate.getFullYear() - 100);
    const maxDate = new Date();
    maxDate.setFullYear(maxDate.getFullYear() - 5);
    
    if (birthDate < minDate || birthDate > maxDate) {
        return 'Data de nascimento deve ser de pelo menos 5 anos atrás';
    }
    
    // Validação de email
    if (data.email && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.email)) {
        return 'Email inválido';
    }
    
    // Validação de status
    if (!data.status || !['ativo', 'inativo'].includes(data.status)) {
        return 'Status deve ser ativo ou inativo';
    }
    
    return null;
}

function calculateAge(birthDate) {
    const today = new Date();
    const birth = new Date(birthDate);
    let age = today.getFullYear() - birth.getFullYear();
    const monthDiff = today.getMonth() - birth.getMonth();
    
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
        age--;
    }
    
    return age;
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('pt-BR');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function capitalize(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

function trapFocus(element) {
    const focusableElements = element.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    
    const firstElement = focusableElements[0];
    const lastElement = focusableElements[focusableElements.length - 1];
    
    element.addEventListener('keydown', (e) => {
        if (e.key === 'Tab') {
            if (e.shiftKey) {
                if (document.activeElement === firstElement) {
                    lastElement.focus();
                    e.preventDefault();
                }
            } else {
                if (document.activeElement === lastElement) {
                    firstElement.focus();
                    e.preventDefault();
                }
            }
        }
    });
}

function announceToScreenReader(message) {
    const announcement = document.createElement('div');
    announcement.setAttribute('aria-live', 'polite');
    announcement.setAttribute('aria-atomic', 'true');
    announcement.className = 'sr-only';
    announcement.textContent = message;
    
    document.body.appendChild(announcement);
    
    setTimeout(() => {
        document.body.removeChild(announcement);
    }, 1000);
}

function handleKeyboardShortcuts(e) {
    // Alt + N = Novo Aluno
    if (e.altKey && e.key === 'n' && currentTab === 'alunos') {
        e.preventDefault();
        openModal('modalNovoAluno');
    }
    
    // Alt + T = Nova Turma
    if (e.altKey && e.key === 't' && currentTab === 'turmas') {
        e.preventDefault();
        openModal('modalNovaTurma');
    }
    
    // Alt + 1, 2, 3 = Trocar tabs
    if (e.altKey && ['1', '2', '3'].includes(e.key)) {
        e.preventDefault();
        const tabs = ['alunos', 'turmas', 'relatorios'];
        const index = parseInt(e.key) - 1;
        if (tabs[index]) {
            switchTab(tabs[index]);
        }
    }
}

function handleExport() {
    if (currentTab === 'alunos') {
        exportData('alunos', 'csv');
    } else if (currentTab === 'turmas') {
        exportData('turmas', 'json');
    }
}
