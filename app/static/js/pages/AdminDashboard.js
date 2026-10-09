import { ref, onMounted } from "vue";
import { api } from "../api.js";

export default {
  setup() {
    const tab = ref("Companies");
    const tabs = ["Companies", "Students", "Drives"];
    const statCards = ref([]);
    const companies = ref([]);
    const companyQuery = ref("");
    const students = ref([]);
    const studentQuery = ref("");
    const drives = ref([]);

    function badgeClass(status) {
      return {
        approved: "bg-success", pending: "bg-warning text-dark",
        rejected: "bg-danger", closed: "bg-secondary",
      }[status] || "bg-secondary";
    }

    async function loadStats() {
      const s = await api.get("/api/admin/stats");
      statCards.value = [
        { label: "Total Students", value: s.total_students },
        { label: "Approved Companies", value: s.total_companies },
        { label: "Total Drives", value: s.total_drives },
        { label: "Total Selected", value: s.total_selected },
      ];
    }
    async function loadCompanies() {
      companies.value = await api.get("/api/admin/companies?q=" + encodeURIComponent(companyQuery.value));
    }
    async function loadStudents() {
      students.value = await api.get("/api/admin/students?q=" + encodeURIComponent(studentQuery.value));
    }
    async function loadDrives() {
      drives.value = await api.get("/api/admin/drives");
    }
    async function approveCompany(id) { await api.post(`/api/admin/companies/${id}/approve`); await loadCompanies(); await loadStats(); }
    async function rejectCompany(id) { await api.post(`/api/admin/companies/${id}/reject`); await loadCompanies(); await loadStats(); }
    async function toggleBlacklistCompany(id) { await api.post(`/api/admin/companies/${id}/blacklist`); await loadCompanies(); }
    async function toggleStudentActive(id) { await api.post(`/api/admin/students/${id}/toggle-active`); await loadStudents(); }
    async function approveDrive(id) { await api.post(`/api/admin/drives/${id}/approve`); await loadDrives(); await loadStats(); }
    async function rejectDrive(id) { await api.post(`/api/admin/drives/${id}/reject`); await loadDrives(); await loadStats(); }

    onMounted(async () => {
      await loadStats();
      await Promise.all([loadCompanies(), loadStudents(), loadDrives()]);
    });

    return {
      tab, tabs, statCards, companies, companyQuery, students, studentQuery, drives,
      badgeClass, loadCompanies, loadStudents, loadDrives,
      approveCompany, rejectCompany, toggleBlacklistCompany, toggleStudentActive,
      approveDrive, rejectDrive,
    };
  },
  template: `
    <div class="container">
      <div class="row g-3 mb-4">
        <div class="col-md-3 col-6" v-for="s in statCards" :key="s.label">
          <div class="card stat-card p-3 text-center">
            <div class="text-muted small">{{ s.label }}</div>
            <h2>{{ s.value }}</h2>
          </div>
        </div>
      </div>

      <ul class="nav nav-tabs mb-3">
        <li class="nav-item" v-for="t in tabs" :key="t">
          <a class="nav-link" :class="{active: tab===t}" href="#" @click.prevent="tab=t">{{ t }}</a>
        </li>
      </ul>

      <div v-if="tab==='Companies'" class="card p-3">
        <div class="d-flex mb-3">
          <input v-model="companyQuery" @input="loadCompanies" class="form-control" placeholder="Search companies...">
        </div>
        <table class="table table-sm align-middle">
          <thead><tr><th>Name</th><th>Contact</th><th>Status</th><th>Blacklisted</th><th>Actions</th></tr></thead>
          <tbody>
            <tr v-for="c in companies" :key="c.id">
              <td>{{ c.company_name }}</td>
              <td>{{ c.user.email }}</td>
              <td><span class="badge" :class="badgeClass(c.approval_status)">{{ c.approval_status }}</span></td>
              <td>{{ c.user.is_blacklisted ? 'Yes' : 'No' }}</td>
              <td class="table-actions">
                <button class="btn btn-sm btn-success" v-if="c.approval_status!=='approved'" @click="approveCompany(c.id)">Approve</button>
                <button class="btn btn-sm btn-danger" v-if="c.approval_status!=='rejected'" @click="rejectCompany(c.id)">Reject</button>
                <button class="btn btn-sm btn-outline-dark" @click="toggleBlacklistCompany(c.id)">Toggle Blacklist</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="tab==='Students'" class="card p-3">
        <div class="d-flex mb-3">
          <input v-model="studentQuery" @input="loadStudents" class="form-control" placeholder="Search students...">
        </div>
        <table class="table table-sm align-middle">
          <thead><tr><th>Name</th><th>Email</th><th>Branch</th><th>CGPA</th><th>Active</th><th>Actions</th></tr></thead>
          <tbody>
            <tr v-for="s in students" :key="s.id">
              <td>{{ s.user.name }}</td>
              <td>{{ s.user.email }}</td>
              <td>{{ s.branch }}</td>
              <td>{{ s.cgpa }}</td>
              <td>{{ s.user.is_active ? 'Yes' : 'No' }}</td>
              <td><button class="btn btn-sm btn-outline-dark" @click="toggleStudentActive(s.id)">Toggle Active/Deactivate</button></td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="tab==='Drives'" class="card p-3">
        <table class="table table-sm align-middle">
          <thead><tr><th>Title</th><th>Company</th><th>Deadline</th><th>Status</th><th>Applicants</th><th>Actions</th></tr></thead>
          <tbody>
            <tr v-for="d in drives" :key="d.id">
              <td>{{ d.job_title }}</td>
              <td>{{ d.company_name }}</td>
              <td>{{ new Date(d.application_deadline).toLocaleString() }}</td>
              <td><span class="badge" :class="badgeClass(d.status)">{{ d.status }}</span></td>
              <td>{{ d.applicant_count }}</td>
              <td class="table-actions">
                <button class="btn btn-sm btn-success" v-if="d.status!=='approved'" @click="approveDrive(d.id)">Approve</button>
                <button class="btn btn-sm btn-danger" v-if="d.status!=='rejected'" @click="rejectDrive(d.id)">Reject</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  `,
};
