'use strict';

class APIClient {
    constructor() {
        this.token = localStorage.getItem('daa_token') || null;
    }

    setToken(t) {
        this.token = t;
        if (t) localStorage.setItem('daa_token', t);
        else localStorage.removeItem('daa_token');
    }

    _headers(multipart = false) {
        const h = {};
        if (this.token) h['Authorization'] = `Bearer ${this.token}`;
        if (!multipart) h['Content-Type'] = 'application/json';
        return h;
    }

    async _req(method, path, body = null, multipart = false) {
        const opts = { method, headers: this._headers(multipart) };
        if (body) opts.body = multipart ? body : JSON.stringify(body);

        const res = await fetch(path, opts);
        if (res.status === 204) return null;
        const data = await res.json().catch(() => ({ detail: `HTTP ${res.status}` }));
        if (!res.ok) throw new Error(data.detail || `Error ${res.status}`);
        return data;
    }

    // AUTH
    async login(email, password) {
        const d = await this._req('POST', '/auth/login', { email, password });
        this.setToken(d.access_token);
        return d;
    }
    async getMe()  { return this._req('GET', '/auth/me'); }
    logout()       { this.setToken(null); }

    // USERS
    async getUsers()                  { return this._req('GET', '/users'); }
    async createUser(d)               { return this._req('POST', '/users', d); }
    async assignRole(uid, role)       { return this._req('POST', `/users/${uid}/roles/${role}`); }
    async removeRole(uid, role)       { return this._req('DELETE', `/users/${uid}/roles/${role}`); }
    async getRoles()                  { return this._req('GET', '/roles'); }

    // COURSES
    async getCourses()                        { return this._req('GET', '/courses'); }
    async createCourse(d)                     { return this._req('POST', '/courses', d); }
    async getMyCourses()                      { return this._req('GET', '/me/courses'); }
    async getEnrollments(cid)                 { return this._req('GET', `/courses/${cid}/enrollments`); }
    async enrollStudent(cid, sid)             { return this._req('POST', `/courses/${cid}/enrollments`, { student_id: sid }); }
    async removeEnrollment(cid, sid)          { return this._req('DELETE', `/courses/${cid}/enrollments/${sid}`); }

    // QUESTIONS
    async getQuestions()     { return this._req('GET', '/questions'); }
    async createQuestion(d)  { return this._req('POST', '/questions', d); }
    async uploadImage(qid, file) {
        const fd = new FormData();
        fd.append('file', file);
        return this._req('POST', `/questions/${qid}/image`, fd, true);
    }

    // ASSESSMENTS
    async getCourseAssessments(cid)            { return this._req('GET', `/courses/${cid}/assessments`); }
    async createAssessment(cid, d)             { return this._req('POST', `/courses/${cid}/assessments`, d); }
    async getAssessmentQuestions(aid)          { return this._req('GET', `/assessments/${aid}/questions`); }
    async addAssessmentQuestion(aid, d)        { return this._req('POST', `/assessments/${aid}/questions`, d); }
    async removeAssessmentQuestion(aid, aqid)  { return this._req('DELETE', `/assessments/${aid}/questions/${aqid}`); }
    async publishAssessment(aid)               { return this._req('POST', `/assessments/${aid}/publish`); }
    async getForm(aid)                         { return this._req('GET', `/assessments/${aid}/form`); }

    // VISIBILITY RULES
    async createVisibilityRule(aqid, d)  { return this._req('POST', `/assessment-questions/${aqid}/visibility-rule`, d); }
    async deleteVisibilityRule(aqid)     { return this._req('DELETE', `/assessment-questions/${aqid}/visibility-rule`); }

    // ATTEMPTS
    async startAttempt(aid)                { return this._req('POST', `/assessments/${aid}/attempts/start`); }
    async getAttemptForm(tid)              { return this._req('GET', `/attempts/${tid}/form`); }
    async saveAnswers(tid, answers)        { return this._req('POST', `/attempts/${tid}/answers`, { answers }); }
    async submitAttempt(tid)               { return this._req('POST', `/attempts/${tid}/submit`); }
    async getResults(tid)                  { return this._req('GET', `/attempts/${tid}/results`); }
    async getAIFeedback(answerId)          { return this._req('GET', `/question-answers/${answerId}/ai-feedback`); }
}

const api = new APIClient();
