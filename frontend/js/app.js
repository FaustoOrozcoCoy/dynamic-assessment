'use strict';

// ═══════════════════════════════════════════════════
// STATE
// ═══════════════════════════════════════════════════
const S = {
    user: null,
    courseId: null,
    attempt: null,
    answers: {},        // { assessment_question_id: answer_json }
    formQuestions: [],  // cache for take-assessment view
};

// ═══════════════════════════════════════════════════
// UTILITIES
// ═══════════════════════════════════════════════════
const $ = id => document.getElementById(id);
const hasRole = r => S.user?.roles?.includes(r) ?? false;
const isAdmin = () => hasRole('admin');
const isTeacher = () => hasRole('teacher');
const isStudent = () => hasRole('student');
const isStaff = () => isAdmin() || isTeacher();

function esc(str) {
    const d = document.createElement('div');
    d.appendChild(document.createTextNode(String(str ?? '')));
    return d.innerHTML;
}

function setContent(html) { $('content-area').innerHTML = html; }

function spinner() {
    return `<div class="d-flex justify-content-center align-items-center" style="min-height:200px">
        <div class="spinner-border text-primary" role="status"></div>
    </div>`;
}

function toast(msg, type = 'success') {
    const el = document.createElement('div');
    el.className = `toast align-items-center text-white bg-${type === 'success' ? 'success' : 'danger'} border-0`;
    el.setAttribute('role', 'alert');
    el.innerHTML = `<div class="d-flex">
        <div class="toast-body">${esc(msg)}</div>
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
    </div>`;
    $('toast-container').appendChild(el);
    const t = new bootstrap.Toast(el, { delay: 4000 });
    t.show();
    el.addEventListener('hidden.bs.toast', () => el.remove());
}

function roleBadge(r) {
    const cls = { admin: 'danger', teacher: 'primary', student: 'success' };
    return `<span class="badge bg-${cls[r] || 'secondary'} me-1">${r}</span>`;
}

function statusBadge(s) {
    const map = {
        draft: ['warning', 'Borrador'], published: ['success', 'Publicada'],
        archived: ['secondary', 'Archivada'], in_progress: ['info', 'En progreso'],
        submitted: ['primary', 'Enviada'], graded: ['success', 'Calificada'],
    };
    const [c, l] = map[s] || ['secondary', s];
    return `<span class="badge bg-${c}">${l}</span>`;
}

function ctag(text, color = 'info') {
    return `<span class="concept-tag text-${color} border-${color} me-1">${text}</span>`;
}

function fmtDate(iso) {
    if (!iso) return '—';
    return new Date(iso).toLocaleString('es-CO', { dateStyle: 'short', timeStyle: 'short' });
}

function qTypeLabel(t) {
    return { single_choice: 'Única', multiple_choice: 'Múltiple', open_text: 'Texto abierto',
             number: 'Numérico', boolean: 'V/F', scale: 'Escala' }[t] || t;
}

// ═══════════════════════════════════════════════════
// NAVIGATION
// ═══════════════════════════════════════════════════
function navigate(view, params = {}) {
    document.querySelectorAll('.nav-link[data-view]').forEach(a =>
        a.classList.toggle('active', a.dataset.view === view));
    setContent(spinner());
    ({
        dashboard:        () => renderDashboard(),
        users:            () => renderUsers(),
        courses:          () => renderCourses(),
        questions:        () => renderQuestions(),
        assessments:      () => renderAssessments(params.courseId),
        'assessment-detail': () => renderAssessmentDetail(params.assessmentId, params.courseId),
        'my-assessments': () => renderMyAssessments(),
        'take-assessment': () => renderTakeAssessment(params.assessmentId),
        results:          () => renderResults(params.attemptId),
    }[view] || (() => setContent('<p>Vista no encontrada</p>')))();
}

function showLogin() {
    $('login-screen').classList.remove('d-none');
    $('app').classList.add('d-none');
}

function showApp() {
    $('login-screen').classList.add('d-none');
    $('app').classList.remove('d-none');
    syncSidebar();
}

function syncSidebar() {
    const u = S.user;
    if (!u) return;
    $('sb-name').textContent = u.full_name;
    $('sb-email').textContent = u.email;
    $('sb-roles').innerHTML = u.roles.map(roleBadge).join('');

    const tok = api.token || '';
    $('jwt-preview').textContent = tok.length > 55
        ? tok.slice(0, 25) + ' … ' + tok.slice(-18) : tok;

    const show = (cls, cond) =>
        document.querySelectorAll('.' + cls).forEach(el => el.style.display = cond ? '' : 'none');

    show('staff-item', isStaff());
    show('admin-item', isAdmin());
    show('student-item', isStudent());
    show('staff-section', isStaff());
    show('student-section', isStudent());
}

// ═══════════════════════════════════════════════════
// VIEW: DASHBOARD
// ═══════════════════════════════════════════════════
async function renderDashboard() {
    const u = S.user;
    setContent(`
    <div class="row g-4">
      <div class="col-12">
        <h4 class="mb-0">Dashboard</h4>
        <small class="text-muted">Bienvenido, <strong>${esc(u.full_name)}</strong></small>
      </div>

      <div class="col-md-6">
        <div class="card h-100">
          <div class="card-body">
            <h6 class="text-muted mb-3"><i class="bi bi-person-circle me-2"></i>Tu sesión
              ${ctag('JWT Auth', 'primary')} ${ctag('RBAC', 'danger')}
            </h6>
            <div class="d-flex align-items-center mb-3">
              <div class="rounded-circle bg-primary bg-opacity-10 d-flex align-items-center justify-content-center me-3" style="width:52px;height:52px">
                <i class="bi bi-person fs-4 text-primary"></i>
              </div>
              <div>
                <div class="fw-semibold">${esc(u.full_name)}</div>
                <div class="text-muted small">${esc(u.email)}</div>
                <div class="mt-1">${u.roles.map(roleBadge).join('')}</div>
              </div>
            </div>
            <hr class="my-2">
            <small class="text-muted"><i class="bi bi-key me-1"></i>Token JWT activo · ID: ${u.id}</small>
          </div>
        </div>
      </div>

      <div class="col-md-6">
        <div class="card h-100">
          <div class="card-body">
            <h6 class="text-muted mb-3"><i class="bi bi-cpu me-2"></i>Conceptos del backend demostrados</h6>
            <div class="d-flex flex-wrap gap-2">
              ${ctag('FastAPI + Uvicorn', 'dark')}
              ${ctag('PostgreSQL + SQLAlchemy', 'warning')}
              ${ctag('Alembic (migraciones)', 'secondary')}
              ${ctag('JWT Authentication', 'primary')}
              ${ctag('RBAC (roles)', 'danger')}
              ${ctag('Banco de preguntas reutilizable', 'info')}
              ${ctag('Formularios dinámicos', 'primary')}
              ${ctag('Reglas de visibilidad', 'info')}
              ${ctag('Calificación automática', 'success')}
              ${ctag('Feedback IA (OpenRouter)', 'success')}
              ${ctag('Subida de imágenes', 'warning')}
              ${ctag('Archivos estáticos', 'secondary')}
            </div>
          </div>
        </div>
      </div>

      <div class="col-12">
        <div class="card">
          <div class="card-body">
            <h6 class="text-muted mb-3"><i class="bi bi-lightning me-2"></i>Acciones rápidas</h6>
            <div class="d-flex flex-wrap gap-2">
              ${isAdmin() ? `<button class="btn btn-outline-danger btn-sm" onclick="navigate('users')"><i class="bi bi-people me-1"></i>Usuarios</button>` : ''}
              ${isStaff() ? `<button class="btn btn-outline-primary btn-sm" onclick="navigate('courses')"><i class="bi bi-book me-1"></i>Cursos</button>` : ''}
              ${isStaff() ? `<button class="btn btn-outline-info btn-sm" onclick="navigate('questions')"><i class="bi bi-question-circle me-1"></i>Banco de preguntas</button>` : ''}
              ${isStudent() ? `<button class="btn btn-outline-success btn-sm" onclick="navigate('my-assessments')"><i class="bi bi-clipboard-check me-1"></i>Mis evaluaciones</button>` : ''}
            </div>
          </div>
        </div>
      </div>
    </div>`);
}

// ═══════════════════════════════════════════════════
// VIEW: USERS (admin)
// ═══════════════════════════════════════════════════
async function renderUsers() {
    try {
        const users = await api.getUsers();
        setContent(`
        <div class="d-flex justify-content-between align-items-center mb-4">
          <div>
            <h4 class="mb-0">Usuarios</h4>
            <small class="text-muted">${ctag('RBAC', 'danger')} ${ctag('Gestión de roles', 'dark')}</small>
          </div>
          <button class="btn btn-primary btn-sm" onclick="openModal('modal-create-user')">
            <i class="bi bi-plus-lg me-1"></i>Nuevo usuario
          </button>
        </div>
        <div class="card">
          <div class="table-responsive">
            <table class="table table-hover mb-0">
              <thead class="table-light"><tr>
                <th>ID</th><th>Nombre</th><th>Email</th><th>Roles</th><th>Estado</th><th></th>
              </tr></thead>
              <tbody>
                ${users.map(u => `<tr>
                  <td class="text-muted small">${u.id}</td>
                  <td class="fw-medium">${esc(u.full_name)}</td>
                  <td class="text-muted small">${esc(u.email)}</td>
                  <td>${u.roles.map(roleBadge).join('') || '<span class="text-muted">—</span>'}</td>
                  <td>${u.is_active ? '<span class="badge bg-success">Activo</span>' : '<span class="badge bg-secondary">Inactivo</span>'}</td>
                  <td>
                    <button class="btn btn-outline-secondary btn-sm" title="Asignar rol"
                      onclick="openAssignRole(${u.id}, '${esc(u.full_name)}')">
                      <i class="bi bi-person-gear"></i>
                    </button>
                  </td>
                </tr>`).join('')}
              </tbody>
            </table>
          </div>
        </div>`);
    } catch (e) { toast(e.message, 'error'); setContent(`<div class="alert alert-danger">${esc(e.message)}</div>`); }
}

// ═══════════════════════════════════════════════════
// VIEW: COURSES
// ═══════════════════════════════════════════════════
async function renderCourses() {
    try {
        const courses = await api.getCourses();
        setContent(`
        <div class="d-flex justify-content-between align-items-center mb-4">
          <div>
            <h4 class="mb-0">Cursos</h4>
            <small class="text-muted">${ctag('Gestión académica', 'primary')} ${ctag('Inscripciones', 'info')}</small>
          </div>
          <button class="btn btn-primary btn-sm" onclick="openCreateCourse()">
            <i class="bi bi-plus-lg me-1"></i>Nuevo curso
          </button>
        </div>
        ${courses.length === 0
          ? '<div class="alert alert-info">No hay cursos. Crea el primero.</div>'
          : `<div class="row g-3">${courses.map(c => `
            <div class="col-md-6 col-lg-4">
              <div class="card h-100">
                <div class="card-body">
                  <div class="d-flex justify-content-between align-items-start mb-2">
                    <h6 class="card-title mb-0">${esc(c.name)}</h6>
                    ${c.is_active ? '<span class="badge bg-success">Activo</span>' : '<span class="badge bg-secondary">Inactivo</span>'}
                  </div>
                  <p class="text-muted small mb-3">${esc(c.description || '—')}</p>
                  <div class="d-flex gap-2">
                    <button class="btn btn-primary btn-sm flex-grow-1"
                      onclick="navigate('assessments', {courseId: ${c.id}})">
                      <i class="bi bi-clipboard-check me-1"></i>Evaluaciones
                    </button>
                    <button class="btn btn-outline-secondary btn-sm" title="Inscribir estudiante"
                      onclick="openEnrollStudent(${c.id}, '${esc(c.name)}')">
                      <i class="bi bi-person-plus"></i>
                    </button>
                  </div>
                </div>
              </div>
            </div>`).join('')}</div>`
        }`);
    } catch (e) { toast(e.message, 'error'); setContent(`<div class="alert alert-danger">${esc(e.message)}</div>`); }
}

// ═══════════════════════════════════════════════════
// VIEW: QUESTIONS
// ═══════════════════════════════════════════════════
async function renderQuestions() {
    try {
        const qs = await api.getQuestions();
        setContent(`
        <div class="d-flex justify-content-between align-items-center mb-4">
          <div>
            <h4 class="mb-0">Banco de Preguntas</h4>
            <small class="text-muted">${ctag('Reutilizable', 'info')} ${ctag('Subida de imágenes', 'warning')}</small>
          </div>
          <button class="btn btn-primary btn-sm" onclick="openCreateQuestion()">
            <i class="bi bi-plus-lg me-1"></i>Nueva pregunta
          </button>
        </div>
        ${qs.length === 0
          ? '<div class="alert alert-info">No hay preguntas. Crea la primera.</div>'
          : `<div class="row g-3">${qs.map(q => `
            <div class="col-md-6">
              <div class="card h-100">
                <div class="card-body">
                  <div class="d-flex justify-content-between mb-2">
                    <span class="badge bg-secondary">${qTypeLabel(q.question_type)}</span>
                    <small class="text-muted">ID: ${q.id}</small>
                  </div>
                  <p class="fw-medium mb-2">${esc(q.statement)}</p>
                  ${q.image_path ? `<img src="${q.image_path}" class="q-image" alt="Imagen">` : ''}
                  ${q.options?.length ? `<div class="small text-muted mb-2">
                    ${q.options.slice(0,4).map(o => `<span class="me-2">${o.is_correct ? '✓' : '○'} ${esc(o.label)}</span>`).join('')}
                    ${q.options.length > 4 ? `<em>+${q.options.length - 4} más</em>` : ''}
                  </div>` : ''}
                  <label class="btn btn-outline-secondary btn-sm mt-1" style="cursor:pointer">
                    <i class="bi bi-image me-1"></i>${q.image_path ? 'Cambiar imagen' : 'Subir imagen'}
                    <input type="file" accept="image/*" class="d-none" onchange="uploadImage(${q.id}, this)">
                  </label>
                </div>
              </div>
            </div>`).join('')}</div>`
        }`);
    } catch (e) { toast(e.message, 'error'); setContent(`<div class="alert alert-danger">${esc(e.message)}</div>`); }
}

// ═══════════════════════════════════════════════════
// VIEW: ASSESSMENTS (per course)
// ═══════════════════════════════════════════════════
async function renderAssessments(courseId) {
    try {
        S.courseId = courseId;
        const list = await api.getCourseAssessments(courseId);
        setContent(`
        <nav aria-label="breadcrumb" class="mb-3">
          <ol class="breadcrumb">
            <li class="breadcrumb-item"><a href="#" onclick="navigate('courses');return false">Cursos</a></li>
            <li class="breadcrumb-item active">Evaluaciones</li>
          </ol>
        </nav>
        <div class="d-flex justify-content-between align-items-center mb-4">
          <div>
            <h4 class="mb-0">Evaluaciones del curso</h4>
            <small class="text-muted">${ctag('Formularios dinámicos', 'primary')} ${ctag('Calificación automática', 'success')}</small>
          </div>
          <button class="btn btn-primary btn-sm" onclick="openCreateAssessment(${courseId})">
            <i class="bi bi-plus-lg me-1"></i>Nueva evaluación
          </button>
        </div>
        ${list.length === 0
          ? '<div class="alert alert-info">No hay evaluaciones en este curso.</div>'
          : `<div class="card"><div class="table-responsive">
            <table class="table table-hover mb-0">
              <thead class="table-light"><tr>
                <th>Título</th><th>Tipo</th><th>Estado</th><th>Publicada</th><th>Acciones</th>
              </tr></thead>
              <tbody>${list.map(a => `<tr>
                <td class="fw-medium">${esc(a.title)}</td>
                <td><span class="badge bg-secondary">${a.assessment_type}</span></td>
                <td>${statusBadge(a.status)}</td>
                <td class="small text-muted">${fmtDate(a.published_at)}</td>
                <td>
                  <button class="btn btn-primary btn-sm me-1"
                    onclick="navigate('assessment-detail', {assessmentId: ${a.id}, courseId: ${courseId}})">
                    <i class="bi bi-gear"></i> Gestionar
                  </button>
                  ${a.status === 'draft' ? `
                    <button class="btn btn-success btn-sm" onclick="doPublish(${a.id}, ${courseId})">
                      <i class="bi bi-send"></i> Publicar
                    </button>` : ''}
                </td>
              </tr>`).join('')}</tbody>
            </table>
          </div></div>`
        }`);
    } catch (e) { toast(e.message, 'error'); setContent(`<div class="alert alert-danger">${esc(e.message)}</div>`); }
}

// ═══════════════════════════════════════════════════
// VIEW: ASSESSMENT DETAIL (builder)
// ═══════════════════════════════════════════════════
async function renderAssessmentDetail(assessmentId, courseId) {
    try {
        S.courseId = courseId || S.courseId;
        const [aqs, allQs, assessments] = await Promise.all([
            api.getAssessmentQuestions(assessmentId),
            api.getQuestions(),
            api.getCourseAssessments(S.courseId),
        ]);
        const a = assessments.find(x => x.id === assessmentId) || { id: assessmentId, title: 'Evaluación', status: 'draft', assessment_type: '' };

        setContent(`
        <nav aria-label="breadcrumb" class="mb-3">
          <ol class="breadcrumb">
            <li class="breadcrumb-item"><a href="#" onclick="navigate('courses');return false">Cursos</a></li>
            <li class="breadcrumb-item"><a href="#" onclick="navigate('assessments',{courseId:${S.courseId}});return false">Evaluaciones</a></li>
            <li class="breadcrumb-item active">${esc(a.title)}</li>
          </ol>
        </nav>

        <div class="d-flex justify-content-between align-items-start mb-4">
          <div>
            <h4 class="mb-1">${esc(a.title)}</h4>
            <div>${statusBadge(a.status)} <span class="badge bg-secondary ms-1">${a.assessment_type}</span>
              ${ctag('Formulario dinámico', 'primary')} ${ctag('Reglas de visibilidad', 'info')}
            </div>
          </div>
          <div class="d-flex gap-2">
            ${a.status === 'draft' ? `<button class="btn btn-success btn-sm" onclick="doPublish(${assessmentId}, ${S.courseId})">
              <i class="bi bi-send me-1"></i>Publicar</button>` : ''}
            <button class="btn btn-outline-primary btn-sm"
              onclick="navigate('take-assessment', {assessmentId: ${assessmentId}})"
              ${a.status !== 'published' ? 'disabled title="Publicar primero"' : ''}>
              <i class="bi bi-eye me-1"></i>Vista previa
            </button>
          </div>
        </div>

        <div class="d-flex justify-content-between align-items-center mb-3">
          <h5 class="mb-0">Preguntas (${aqs.length})</h5>
          <button class="btn btn-primary btn-sm"
            onclick='openAddQuestion(${assessmentId}, ${JSON.stringify(allQs).replace(/'/g,"&#39;")})'>
            <i class="bi bi-plus-lg me-1"></i>Agregar pregunta
          </button>
        </div>

        ${aqs.length === 0
          ? '<div class="alert alert-info">Esta evaluación no tiene preguntas. Agrega la primera.</div>'
          : `<div id="aq-list">${aqs.map(aq => buildAQCard(aq, assessmentId, aqs)).join('')}</div>`
        }`);
    } catch (e) { toast(e.message, 'error'); setContent(`<div class="alert alert-danger">${esc(e.message)}</div>`); }
}

function buildAQCard(aq, assessmentId, allAQs) {
    const q = aq.question || {};
    const prev = allAQs.filter(x => x.order_index < aq.order_index);
    return `
    <div class="card mb-3">
      <div class="card-body">
        <div class="d-flex justify-content-between align-items-start">
          <div class="flex-grow-1">
            <div class="d-flex align-items-center gap-2 mb-1">
              <span class="badge bg-dark">#${aq.order_index}</span>
              <span class="badge bg-secondary">${qTypeLabel(q.question_type || '')}</span>
              <span class="text-muted small">${aq.points} pts</span>
              ${aq.is_required ? '<span class="badge bg-danger bg-opacity-10 text-danger border border-danger border-opacity-25 small">Requerida</span>' : ''}
            </div>
            <p class="fw-medium mb-1">${esc(q.statement || '')}</p>
            ${q.image_path ? `<img src="${q.image_path}" style="max-height:70px;border-radius:4px" class="mb-1">` : ''}
            ${q.options?.length ? `<div class="small text-muted">${q.options.slice(0,3).map(o => `${o.is_correct ? '✓' : '○'} ${esc(o.label)}`).join(' · ')}</div>` : ''}
          </div>
          <button class="btn btn-outline-danger btn-sm ms-3" onclick="removeAQ(${assessmentId}, ${aq.id})" title="Eliminar">
            <i class="bi bi-trash"></i>
          </button>
        </div>
        <hr class="my-2">
        <div>
          <small class="text-muted"><i class="bi bi-eye me-1"></i>Regla de visibilidad ${ctag('Formulario dinámico', 'info')}</small>
          ${prev.length === 0
            ? '<div class="mt-1"><small class="text-muted fst-italic">Primera pregunta — no aplica regla.</small></div>'
            : `<div class="mt-2 d-flex gap-2">
                <button class="btn btn-outline-info btn-sm"
                  onclick='openVisibilityRule(${aq.id}, ${assessmentId}, ${JSON.stringify(prev).replace(/'/g,"&#39;")})'>
                  <i class="bi bi-funnel me-1"></i>Configurar regla
                </button>
                <button class="btn btn-outline-danger btn-sm" onclick="deleteVR(${aq.id}, ${assessmentId})">
                  <i class="bi bi-x-circle me-1"></i>Eliminar regla
                </button>
              </div>`
          }
        </div>
      </div>
    </div>`;
}

// ═══════════════════════════════════════════════════
// VIEW: STUDENT — MY ASSESSMENTS
// ═══════════════════════════════════════════════════
async function renderMyAssessments() {
    try {
        const courses = await api.getMyCourses();
        const groups = await Promise.all(
            courses.map(async c => ({
                course: c,
                assessments: (await api.getCourseAssessments(c.id)).filter(a => a.status === 'published'),
            }))
        );

        setContent(`
        <div class="mb-4">
          <h4 class="mb-0">Mis Evaluaciones</h4>
          <small class="text-muted">
            ${ctag('Formularios dinámicos', 'primary')} ${ctag('Reglas de visibilidad', 'info')}
            ${ctag('Guardado parcial', 'warning')} ${ctag('Feedback IA', 'success')}
          </small>
        </div>
        ${groups.length === 0
          ? '<div class="alert alert-info">No estás inscrito en ningún curso.</div>'
          : groups.map(({ course, assessments }) => `
            <h5 class="text-muted mb-3"><i class="bi bi-book me-2"></i>${esc(course.name)}</h5>
            ${assessments.length === 0
              ? '<p class="text-muted small ms-2 mb-4">No hay evaluaciones publicadas.</p>'
              : `<div class="row g-3 mb-4">${assessments.map(a => `
                <div class="col-md-6">
                  <div class="card">
                    <div class="card-body">
                      <div class="d-flex justify-content-between mb-2">
                        <h6 class="mb-0">${esc(a.title)}</h6>
                        <span class="badge bg-secondary">${a.assessment_type}</span>
                      </div>
                      ${a.description ? `<p class="small text-muted mb-3">${esc(a.description)}</p>` : ''}
                      <button class="btn btn-primary btn-sm w-100"
                        onclick="navigate('take-assessment', {assessmentId: ${a.id}})">
                        <i class="bi bi-play me-1"></i>Iniciar / Continuar
                      </button>
                    </div>
                  </div>
                </div>`).join('')}</div>`
            }`).join('')
        }`);
    } catch (e) { toast(e.message, 'error'); setContent(`<div class="alert alert-danger">${esc(e.message)}</div>`); }
}

// ═══════════════════════════════════════════════════
// VIEW: TAKE ASSESSMENT (dynamic form)
// ═══════════════════════════════════════════════════
async function renderTakeAssessment(assessmentId) {
    try {
        const attempt = await api.startAttempt(assessmentId);
        S.attempt = attempt;

        if (attempt.status === 'submitted' || attempt.status === 'graded') {
            toast('Esta evaluación ya fue enviada.', 'error');
            navigate('results', { attemptId: attempt.id });
            return;
        }

        const af = await api.getAttemptForm(attempt.id);
        S.answers = { ...af.saved_answers };
        S.formQuestions = af.form.questions;
        paintForm(af, attempt);
    } catch (e) { toast(e.message, 'error'); setContent(`<div class="alert alert-danger">${esc(e.message)}</div>`); }
}

function paintForm(af, attempt) {
    const { form } = af;
    const vis = computeVisibility(S.formQuestions, S.answers);

    setContent(`
    <div class="d-flex justify-content-between align-items-start mb-3">
      <div>
        <h4 class="mb-1">${esc(form.title)}</h4>
        <div>${statusBadge(attempt.status)} ${ctag('Reglas de visibilidad', 'info')} ${ctag('Guardado parcial', 'warning')}</div>
      </div>
      <div class="d-flex gap-2">
        <button class="btn btn-outline-primary btn-sm" onclick="doSave()"><i class="bi bi-floppy me-1"></i>Guardar</button>
        <button class="btn btn-success btn-sm" onclick="doSubmit()"><i class="bi bi-check-lg me-1"></i>Enviar</button>
      </div>
    </div>

    <div class="alert alert-info py-2 mb-3" role="alert">
      <i class="bi bi-info-circle me-2"></i>
      <small><strong>Formulario dinámico:</strong> las preguntas con reglas de visibilidad aparecen según tus respuestas. El backend también valida estas reglas al enviar.</small>
    </div>

    <div id="form-body">
      ${form.questions.map(q => buildFormQ(q, vis[q.assessment_question_id])).join('')}
    </div>

    <div class="d-flex justify-content-end gap-2 mt-4">
      <button class="btn btn-outline-primary" onclick="doSave()"><i class="bi bi-floppy me-1"></i>Guardar progreso</button>
      <button class="btn btn-success" onclick="doSubmit()"><i class="bi bi-send me-1"></i>Enviar evaluación</button>
    </div>`);
}

function buildFormQ(q, visible) {
    const saved = S.answers[q.assessment_question_id];
    return `
    <div class="question-card ${visible ? '' : 'hidden-q'}" id="fq-${q.assessment_question_id}"
         style="${visible ? '' : 'display:none'}">
      ${q.visibility_rule ? `<div class="mb-1"><small class="text-info"><i class="bi bi-eye me-1"></i>Visible condicionalmente</small></div>` : ''}
      <div class="d-flex justify-content-between align-items-start mb-2">
        <label class="form-label fw-medium mb-0">
          ${q.is_required ? '<span class="text-danger me-1">*</span>' : ''}${esc(q.statement)}
        </label>
        <small class="text-muted ms-3 text-nowrap">${q.points} pts</small>
      </div>
      ${q.image_path ? `<img src="${q.image_path}" class="q-image" alt="Imagen">` : ''}
      ${buildInput(q, saved)}
    </div>`;
}

function buildInput(q, saved) {
    const id = q.assessment_question_id;
    switch (q.question_type) {
        case 'single_choice':
            return `<div class="mt-2">${q.options.map(o => `
              <div class="ans-option ${saved === o.value ? 'selected' : ''}"
                   onclick="pickSingle(${id}, '${esc(o.value)}', this)">
                <div class="form-check mb-0">
                  <input type="radio" class="form-check-input" name="q${id}" value="${esc(o.value)}" ${saved === o.value ? 'checked' : ''}>
                  <label class="form-check-label">${esc(o.label)}</label>
                </div>
              </div>`).join('')}</div>`;

        case 'multiple_choice': {
            const arr = Array.isArray(saved) ? saved : [];
            return `<div class="mt-2">${q.options.map(o => `
              <div class="ans-option ${arr.includes(o.value) ? 'selected' : ''}"
                   onclick="pickMulti(${id}, '${esc(o.value)}', this)">
                <div class="form-check mb-0">
                  <input type="checkbox" class="form-check-input" value="${esc(o.value)}" ${arr.includes(o.value) ? 'checked' : ''}>
                  <label class="form-check-label">${esc(o.label)}</label>
                </div>
              </div>`).join('')}</div>`;
        }

        case 'boolean':
            return `<div class="d-flex gap-2 mt-2">
              ${[{l:'Verdadero',v:'true'},{l:'Falso',v:'false'}].map(o => `
                <div class="ans-option flex-grow-1 text-center ${saved === o.v ? 'selected' : ''}"
                     onclick="pickSingle(${id}, '${o.v}', this)">
                  <input type="radio" class="d-none" name="q${id}" value="${o.v}" ${saved === o.v ? 'checked' : ''}>
                  ${o.l}
                </div>`).join('')}
            </div>`;

        case 'open_text': {
            const min = q.config_json?.min_length || 0;
            const max = q.config_json?.max_length || 2000;
            return `<div class="mt-2">
              <textarea class="form-control" rows="4" maxlength="${max}"
                placeholder="Escribe tu respuesta aquí..."
                oninput="setAns(${id}, this.value)"
                onblur="setAns(${id}, this.value)">${esc(saved || '')}</textarea>
              <small class="text-muted">${min > 0 ? `Mín. ${min} · ` : ''}Máx. ${max} caracteres · ${ctag('Feedback IA · OpenRouter', 'success')}</small>
            </div>`;
        }

        case 'number': {
            const mn = q.config_json?.min, mx = q.config_json?.max;
            return `<div class="mt-2">
              <input type="number" class="form-control" value="${saved ?? ''}"
                ${mn !== undefined ? `min="${mn}"` : ''} ${mx !== undefined ? `max="${mx}"` : ''}
                oninput="setAns(${id}, this.value === '' ? null : Number(this.value))"
                onblur="setAns(${id}, this.value === '' ? null : Number(this.value))">
              ${mn !== undefined ? `<small class="text-muted">Rango: ${mn} – ${mx}</small>` : ''}
            </div>`;
        }

        case 'scale': {
            const mn = q.config_json?.min || 1, mx = q.config_json?.max || 5;
            const vals = Array.from({length: mx - mn + 1}, (_, i) => mn + i);
            return `<div class="d-flex gap-2 flex-wrap mt-2">
              ${vals.map(v => `
                <div class="ans-option text-center px-3 ${saved == v ? 'selected' : ''}"
                     onclick="pickSingle(${id}, ${v}, this)">
                  <input type="radio" class="d-none" name="q${id}" value="${v}" ${saved == v ? 'checked' : ''}>
                  <strong>${v}</strong>
                </div>`).join('')}
            </div><small class="text-muted">${mn} = mínimo, ${mx} = máximo</small>`;
        }

        default:
            return `<input type="text" class="form-control mt-2" value="${esc(saved || '')}"
              onblur="setAns(${id}, this.value)">`;
    }
}

// Answer interaction helpers
function setAns(id, val) { S.answers[id] = val; refreshVisibility(); }

function pickSingle(id, val, el) {
    S.answers[id] = val;
    el.closest('.question-card').querySelectorAll('.ans-option').forEach(o => o.classList.remove('selected'));
    el.classList.add('selected');
    el.querySelector('input[type="radio"]').checked = true;
    refreshVisibility();
}

function pickMulti(id, val, el) {
    let arr = Array.isArray(S.answers[id]) ? [...S.answers[id]] : [];
    const cb = el.querySelector('input[type="checkbox"]');
    if (arr.includes(val)) { arr = arr.filter(v => v !== val); cb.checked = false; el.classList.remove('selected'); }
    else { arr.push(val); cb.checked = true; el.classList.add('selected'); }
    S.answers[id] = arr;
    refreshVisibility();
}

function refreshVisibility() {
    const vis = computeVisibility(S.formQuestions, S.answers);
    S.formQuestions.forEach(q => {
        const el = document.getElementById(`fq-${q.assessment_question_id}`);
        if (!el) return;
        const show = vis[q.assessment_question_id];
        el.style.display = show ? '' : 'none';
        el.classList.toggle('hidden-q', !show);
    });
}

function computeVisibility(questions, answers) {
    const vis = {};
    questions.forEach(q => {
        if (!q.visibility_rule) { vis[q.assessment_question_id] = true; return; }
        const r = q.visibility_rule;
        const ans = answers[r.depends_on_assessment_question_id];
        vis[q.assessment_question_id] = ans !== undefined && ans !== null && evalRule(r.operator, ans, r.expected_value_json);
    });
    return vis;
}

function evalRule(op, ans, exp) {
    switch (op) {
        case 'equals':       return String(ans) === String(exp);
        case 'not_equals':   return String(ans) !== String(exp);
        case 'contains':     return Array.isArray(ans) ? ans.map(String).includes(String(exp)) : String(ans).includes(String(exp));
        case 'greater_than': return Number(ans) > Number(exp);
        case 'less_than':    return Number(ans) < Number(exp);
        default:             return true;
    }
}

async function doSave() {
    if (!S.attempt) return;
    try {
        const answers = Object.entries(S.answers).map(([k, v]) => ({ assessment_question_id: parseInt(k), answer_json: v }));
        await api.saveAnswers(S.attempt.id, answers);
        toast('Progreso guardado');
    } catch (e) { toast(e.message, 'error'); }
}

async function doSubmit() {
    if (!S.attempt) return;
    if (!confirm('¿Enviar la evaluación? No podrás modificar las respuestas después.')) return;
    try {
        const answers = Object.entries(S.answers).map(([k, v]) => ({ assessment_question_id: parseInt(k), answer_json: v }));
        if (answers.length) await api.saveAnswers(S.attempt.id, answers);
        await api.submitAttempt(S.attempt.id);
        toast('¡Evaluación enviada! Procesando resultados...');
        navigate('results', { attemptId: S.attempt.id });
    } catch (e) { toast(e.message, 'error'); }
}

// ═══════════════════════════════════════════════════
// VIEW: RESULTS
// ═══════════════════════════════════════════════════
async function renderResults(attemptId) {
    try {
        const [result, af] = await Promise.all([api.getResults(attemptId), api.getAttemptForm(attemptId)]);
        const form = af.form;
        const saved = af.saved_answers;
        const answerIds = af.answer_ids || {};

        // Fetch AI feedback in parallel for all open_text answers that exist
        const feedbackMap = {};
        await Promise.all(
            form.questions
                .filter(q => q.question_type === 'open_text')
                .map(async q => {
                    const answerId = answerIds[q.assessment_question_id];
                    if (!answerId) return;
                    try {
                        feedbackMap[q.assessment_question_id] = await api.getAIFeedback(answerId);
                    } catch (_) {
                        feedbackMap[q.assessment_question_id] = null;
                    }
                })
        );

        setContent(`
        <div class="mb-4">
          <h4 class="mb-1">Resultados: ${esc(form.title)}</h4>
          <div>${statusBadge(result.status)} ${ctag('Calificación automática', 'success')} ${ctag('Feedback IA · OpenRouter', 'primary')}</div>
        </div>

        <div class="card mb-4 text-center border-0 shadow-sm">
          <div class="card-body py-4">
            <div class="display-5 fw-bold ${result.score !== null ? 'text-success' : 'text-muted'}">
              ${result.score !== null ? result.score.toFixed(2) : '—'}
            </div>
            <div class="text-muted">Puntaje total</div>
            <div class="mt-2">${statusBadge(result.status)}</div>
            ${result.submitted_at ? `<small class="text-muted d-block mt-1">Enviada: ${fmtDate(result.submitted_at)}</small>` : ''}
            ${result.graded_at ? `<small class="text-muted">Calificada: ${fmtDate(result.graded_at)}</small>` : ''}
          </div>
        </div>

        <h5 class="mb-3">Revisión de respuestas</h5>
        ${form.questions.map(q => {
            const ans = saved[q.assessment_question_id];
            const fb  = feedbackMap[q.assessment_question_id];
            return `<div class="card mb-3">
              <div class="card-body">
                <div class="d-flex justify-content-between mb-2">
                  <span class="badge bg-secondary">${qTypeLabel(q.question_type)}</span>
                  <small class="text-muted">${q.points} pts</small>
                </div>
                <p class="fw-medium mb-2">${esc(q.statement)}</p>
                ${q.image_path ? `<img src="${q.image_path}" class="q-image">` : ''}
                <div class="p-2 bg-light rounded border-start border-4 border-primary mb-2">
                  <small class="text-muted d-block mb-1">Tu respuesta:</small>
                  ${fmtAnswer(ans, q)}
                </div>
                ${q.question_type === 'open_text' ? renderAIFeedback(fb) : ''}
              </div>
            </div>`;
        }).join('')}`);
    } catch (e) { toast(e.message, 'error'); setContent(`<div class="alert alert-danger">${esc(e.message)}</div>`); }
}

function renderAIFeedback(fb) {
    if (!fb) {
        return `<div class="p-2 bg-warning bg-opacity-10 rounded border-start border-4 border-warning">
          <small class="text-warning"><i class="bi bi-robot me-1"></i><strong>Feedback IA</strong></small>
          <p class="mb-0 mt-1 small text-muted">No hay feedback generado para esta respuesta.</p>
        </div>`;
    }
    if (fb.status === 'pending') {
        return `<div class="p-2 bg-info bg-opacity-10 rounded border-start border-4 border-info">
          <small class="text-info"><i class="bi bi-robot me-1"></i><strong>Feedback IA</strong></small>
          <p class="mb-0 mt-1 small text-muted">
            <span class="spinner-border spinner-border-sm me-1"></span>Generando feedback…
          </p>
        </div>`;
    }
    if (fb.status === 'failed' || !fb.feedback_text) {
        return `<div class="p-2 bg-danger bg-opacity-10 rounded border-start border-4 border-danger">
          <small class="text-danger"><i class="bi bi-robot me-1"></i><strong>Feedback IA</strong></small>
          <p class="mb-0 mt-1 small text-muted">No se pudo generar el feedback automático.</p>
        </div>`;
    }
    return `<div class="p-2 bg-success bg-opacity-10 rounded border-start border-4 border-success">
      <div class="d-flex justify-content-between align-items-center mb-1">
        <small class="text-success fw-semibold"><i class="bi bi-robot me-1"></i>Feedback IA (OpenRouter)</small>
        <small class="text-muted">${esc(fb.model_name)}</small>
      </div>
      <p class="mb-0 small" style="white-space:pre-wrap">${esc(fb.feedback_text)}</p>
    </div>`;
}

function fmtAnswer(ans, q) {
    if (ans === undefined || ans === null) return '<em class="text-muted">Sin respuesta</em>';
    if (Array.isArray(ans)) {
        const labels = ans.map(v => { const o = q.options?.find(x => x.value === v); return o ? o.label : v; });
        return labels.map(l => `<span class="badge bg-primary me-1">${esc(l)}</span>`).join('');
    }
    if (q.question_type === 'single_choice' || q.question_type === 'boolean') {
        const o = q.options?.find(x => x.value === String(ans));
        return `<span class="badge bg-primary">${esc(o ? o.label : String(ans))}</span>`;
    }
    if (q.question_type === 'open_text') return `<p class="mb-0 small">${esc(String(ans))}</p>`;
    return `<strong>${esc(String(ans))}</strong>`;
}

// ═══════════════════════════════════════════════════
// MODAL HELPERS
// ═══════════════════════════════════════════════════
function openModal(id) { new bootstrap.Modal($(id)).show(); }
function closeModal(id) { bootstrap.Modal.getInstance($(id))?.hide(); }

// --- Create User ---
async function submitCreateUser(e) {
    e.preventDefault();
    const f = e.target;
    const roles = Array.from(f.querySelectorAll('input[name="roles"]:checked')).map(c => c.value);
    try {
        await api.createUser({ email: f.email.value, full_name: f.full_name.value, password: f.password.value, roles });
        toast('Usuario creado');
        closeModal('modal-create-user');
        f.reset();
        navigate('users');
    } catch (e) { toast(e.message, 'error'); }
}

// --- Assign Role ---
function openAssignRole(uid, name) {
    $('ar-uid').value = uid;
    $('ar-name').textContent = name;
    openModal('modal-assign-role');
}
async function submitAssignRole(e) {
    e.preventDefault();
    const uid = $('ar-uid').value;
    const role = e.target.role.value;
    try {
        await api.assignRole(uid, role);
        toast(`Rol '${role}' asignado`);
        closeModal('modal-assign-role');
        navigate('users');
    } catch (e) { toast(e.message, 'error'); }
}

// --- Create Course ---
async function openCreateCourse() {
    if (isAdmin()) {
        try {
            const users = await api.getUsers();
            const teachers = users.filter(u => u.roles.includes('teacher'));
            $('course-teacher-sel').innerHTML = teachers.map(t => `<option value="${t.id}">${esc(t.full_name)}</option>`).join('');
            $('course-teacher-row').style.display = '';
        } catch (_) { $('course-teacher-row').style.display = 'none'; }
    } else { $('course-teacher-row').style.display = 'none'; }
    openModal('modal-create-course');
}
async function submitCreateCourse(e) {
    e.preventDefault();
    const f = e.target;
    const d = { name: f.c_name.value, description: f.c_desc.value || null };
    if (isAdmin() && f.teacher_id?.value) d.teacher_id = parseInt(f.teacher_id.value);
    try {
        await api.createCourse(d);
        toast('Curso creado');
        closeModal('modal-create-course');
        f.reset();
        navigate('courses');
    } catch (e) { toast(e.message, 'error'); }
}

// --- Enroll Student ---
async function openEnrollStudent(cid, cname) {
    $('enroll-cid').value = cid;
    $('enroll-cname').textContent = cname;
    try {
        const users = await api.getUsers();
        const students = users.filter(u => u.roles.includes('student'));
        $('enroll-student-sel').innerHTML = students.map(s => `<option value="${s.id}">${esc(s.full_name)} (${esc(s.email)})</option>`).join('');
    } catch (_) {}
    openModal('modal-enroll-student');
}
async function submitEnroll(e) {
    e.preventDefault();
    const cid = $('enroll-cid').value;
    const sid = $('enroll-student-sel').value;
    try {
        await api.enrollStudent(cid, sid);
        toast('Estudiante inscrito');
        closeModal('modal-enroll-student');
    } catch (e) { toast(e.message, 'error'); }
}

// --- Create Question ---
let _optCount = 0;
function openCreateQuestion() { openModal('modal-create-question'); onQTypeChange(); }
function onQTypeChange() {
    const t = $('q-type').value;
    const hasOpts = ['single_choice', 'multiple_choice', 'boolean'].includes(t);
    $('q-opts-section').style.display = hasOpts ? '' : 'none';
    $('q-cfg-section').style.display = ['number', 'scale', 'open_text'].includes(t) ? '' : 'none';

    let cfgHtml = '';
    if (t === 'number')
        cfgHtml = `<div class="row g-2">
          <div class="col"><input type="number" class="form-control form-control-sm" id="cfg0" placeholder="Mínimo"></div>
          <div class="col"><input type="number" class="form-control form-control-sm" id="cfg1" placeholder="Máximo"></div>
          <div class="col"><input type="number" class="form-control form-control-sm" id="cfg2" placeholder="Tolerancia" step="0.01"></div>
        </div>`;
    else if (t === 'scale')
        cfgHtml = `<div class="row g-2">
          <div class="col"><input type="number" class="form-control form-control-sm" id="cfg0" placeholder="Mínimo" value="1"></div>
          <div class="col"><input type="number" class="form-control form-control-sm" id="cfg1" placeholder="Máximo" value="5"></div>
        </div>`;
    else if (t === 'open_text')
        cfgHtml = `<div class="row g-2">
          <div class="col"><input type="number" class="form-control form-control-sm" id="cfg0" placeholder="Long. mínima" value="20"></div>
          <div class="col"><input type="number" class="form-control form-control-sm" id="cfg1" placeholder="Long. máxima" value="1000"></div>
        </div>`;

    $('q-cfg-fields').innerHTML = cfgHtml;

    if (t === 'boolean') {
        $('q-opts-container').innerHTML = `
          <div class="d-flex gap-2 align-items-center mb-1 p-2 bg-light rounded">
            <input class="form-control form-control-sm" value="Verdadero" readonly style="max-width:120px">
            <input class="form-control form-control-sm" value="true" readonly style="max-width:80px">
            <span class="badge bg-success">Correcta</span>
          </div>
          <div class="d-flex gap-2 align-items-center p-2 bg-light rounded">
            <input class="form-control form-control-sm" value="Falso" readonly style="max-width:120px">
            <input class="form-control form-control-sm" value="false" readonly style="max-width:80px">
            <span class="badge bg-secondary">Incorrecta</span>
          </div>`;
    }
}

function addQOption() {
    _optCount++;
    const n = _optCount;
    const d = document.createElement('div');
    d.id = `opt-${n}`;
    d.className = 'd-flex gap-2 align-items-center mb-2';
    d.innerHTML = `
      <input type="text" class="form-control form-control-sm" id="ol-${n}" placeholder="Etiqueta">
      <input type="text" class="form-control form-control-sm" id="ov-${n}" placeholder="Valor" style="max-width:90px">
      <label class="d-flex align-items-center gap-1 text-nowrap small">
        <input type="checkbox" id="oc-${n}"> ✓ Correcta
      </label>
      <button type="button" class="btn btn-outline-danger btn-sm" onclick="document.getElementById('opt-${n}').remove()">
        <i class="bi bi-trash"></i>
      </button>`;
    $('q-opts-container').appendChild(d);
}

async function submitCreateQuestion(e) {
    e.preventDefault();
    const t = $('q-type').value;

    let options = [];
    if (['single_choice', 'multiple_choice'].includes(t)) {
        const items = $('q-opts-container').querySelectorAll('[id^="opt-"]');
        let i = 1;
        for (const item of items) {
            const n = item.id.replace('opt-', '');
            options.push({
                label: document.getElementById(`ol-${n}`)?.value || '',
                value: document.getElementById(`ov-${n}`)?.value || '',
                is_correct: document.getElementById(`oc-${n}`)?.checked ?? false,
                is_exclusive: false,
                order_index: i++,
            });
        }
    } else if (t === 'boolean') {
        options = [
            { label: 'Verdadero', value: 'true', is_correct: true, is_exclusive: false, order_index: 1 },
            { label: 'Falso', value: 'false', is_correct: false, is_exclusive: false, order_index: 2 },
        ];
    }

    let config_json = null;
    const c0 = $('cfg0'), c1 = $('cfg1'), c2 = $('cfg2');
    if (t === 'number' && c0) {
        config_json = {};
        if (c0.value !== '') config_json.min = parseFloat(c0.value);
        if (c1?.value !== '') config_json.max = parseFloat(c1.value);
        if (c2?.value !== '') config_json.tolerance = parseFloat(c2.value);
    } else if (t === 'scale' && c0) {
        config_json = { min: parseInt(c0.value || 1), max: parseInt(c1?.value || 5) };
    } else if (t === 'open_text' && c0) {
        config_json = {};
        if (c0.value !== '') config_json.min_length = parseInt(c0.value);
        if (c1?.value !== '') config_json.max_length = parseInt(c1.value);
    }

    try {
        await api.createQuestion({ statement: $('q-statement').value, question_type: t, options, config_json });
        toast('Pregunta creada');
        closeModal('modal-create-question');
        e.target.reset();
        $('q-opts-container').innerHTML = '';
        navigate('questions');
    } catch (err) { toast(err.message, 'error'); }
}

async function uploadImage(qid, inputEl) {
    const file = inputEl.files[0];
    if (!file) return;
    try {
        await api.uploadImage(qid, file);
        toast('Imagen actualizada');
        navigate('questions');
    } catch (e) { toast(e.message, 'error'); }
}

// --- Create Assessment ---
function openCreateAssessment(cid) { $('ca-cid').value = cid; openModal('modal-create-assessment'); }
async function submitCreateAssessment(e) {
    e.preventDefault();
    const f = e.target, cid = $('ca-cid').value;
    try {
        await api.createAssessment(cid, { title: f.ca_title.value, assessment_type: f.ca_type.value, description: f.ca_desc.value || null });
        toast('Evaluación creada');
        closeModal('modal-create-assessment');
        f.reset();
        navigate('assessments', { courseId: parseInt(cid) });
    } catch (e) { toast(e.message, 'error'); }
}

// --- Add Question to Assessment ---
function openAddQuestion(aid, questions) {
    $('aq-aid').value = aid;
    const sel = $('aq-qsel');
    sel.innerHTML = questions.map(q =>
        `<option value="${q.id}">[${qTypeLabel(q.question_type)}] ${esc(q.statement.length > 55 ? q.statement.slice(0,55)+'…' : q.statement)}</option>`
    ).join('');
    // Suggest next order index
    openModal('modal-add-question');
}
async function submitAddQuestion(e) {
    e.preventDefault();
    const f = e.target, aid = $('aq-aid').value;
    try {
        await api.addAssessmentQuestion(aid, {
            question_id: parseInt(f.aq_qsel.value),
            order_index: parseInt(f.aq_order.value),
            points: parseFloat(f.aq_points.value),
            is_required: f.aq_required.checked,
        });
        toast('Pregunta agregada');
        closeModal('modal-add-question');
        f.reset();
        navigate('assessment-detail', { assessmentId: parseInt(aid), courseId: S.courseId });
    } catch (e) { toast(e.message, 'error'); }
}

async function removeAQ(aid, aqid) {
    if (!confirm('¿Eliminar esta pregunta de la evaluación?')) return;
    try {
        await api.removeAssessmentQuestion(aid, aqid);
        toast('Pregunta eliminada');
        navigate('assessment-detail', { assessmentId: aid, courseId: S.courseId });
    } catch (e) { toast(e.message, 'error'); }
}

async function doPublish(aid, cid) {
    if (!confirm('¿Publicar? Los estudiantes podrán acceder a esta evaluación.')) return;
    try {
        await api.publishAssessment(aid);
        toast('Evaluación publicada');
        navigate('assessments', { courseId: cid });
    } catch (e) { toast(e.message, 'error'); }
}

// --- Visibility Rules ---
function openVisibilityRule(aqid, aid, prevAQs) {
    $('vr-aqid').value = aqid;
    $('vr-aid').value = aid;
    $('vr-dep-sel').innerHTML = prevAQs.map(aq =>
        `<option value="${aq.id}">[#${aq.order_index}] ${esc((aq.question?.statement || '').slice(0,50))}</option>`
    ).join('');
    openModal('modal-visibility-rule');
}
async function submitVisibilityRule(e) {
    e.preventDefault();
    const f = e.target, aqid = $('vr-aqid').value, aid = $('vr-aid').value;
    let ev;
    try { ev = JSON.parse(f.vr_expected.value); } catch { ev = f.vr_expected.value; }
    try {
        await api.createVisibilityRule(aqid, {
            depends_on_assessment_question_id: parseInt(f.vr_dep.value),
            operator: f.vr_op.value,
            expected_value_json: ev,
        });
        toast('Regla creada');
        closeModal('modal-visibility-rule');
        navigate('assessment-detail', { assessmentId: parseInt(aid), courseId: S.courseId });
    } catch (e) { toast(e.message, 'error'); }
}
async function deleteVR(aqid, aid) {
    try {
        await api.deleteVisibilityRule(aqid);
        toast('Regla eliminada');
        navigate('assessment-detail', { assessmentId: aid, courseId: S.courseId });
    } catch (e) { toast(e.message, 'error'); }
}

// ═══════════════════════════════════════════════════
// AUTH
// ═══════════════════════════════════════════════════
async function handleLogin(e) {
    e.preventDefault();
    const f = e.target, btn = f.querySelector('button[type="submit"]');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Entrando…';
    try {
        await api.login(f.email.value, f.password.value);
        S.user = await api.getMe();
        showApp();
        navigate('dashboard');
    } catch (err) {
        toast(err.message || 'Credenciales incorrectas', 'error');
        btn.disabled = false;
        btn.innerHTML = '<i class="bi bi-box-arrow-in-right me-1"></i>Iniciar sesión';
    }
}

async function quickLogin(email) {
    try {
        await api.login(email, 'password123');
        S.user = await api.getMe();
        showApp();
        navigate('dashboard');
    } catch (e) { toast(e.message || 'Error al iniciar sesión', 'error'); }
}

async function doLogout() {
    api.logout();
    Object.assign(S, { user: null, courseId: null, attempt: null, answers: {}, formQuestions: [] });
    showLogin();
}

// ═══════════════════════════════════════════════════
// INIT
// ═══════════════════════════════════════════════════
async function init() {
    if (api.token) {
        try {
            S.user = await api.getMe();
            showApp();
            navigate('dashboard');
        } catch { api.logout(); showLogin(); }
    } else { showLogin(); }
}

document.addEventListener('DOMContentLoaded', init);
