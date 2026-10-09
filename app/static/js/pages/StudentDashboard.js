import { ref, reactive, onMounted } from "vue";
import { api } from "../api.js";

export default {
  setup() {
    const tab = ref("drives");
    const drives = ref([]);
    const driveQuery = ref("");
    const branchFilter = ref("");
    const applications = ref([]);
    const profile = reactive({});
    const applyError = ref("");
    const profileMsg = ref("");
    const exportMsg = ref("");
    const resumeFile = ref(null);

    function badgeClass(status) {
      return {
        applied: "bg-info text-dark", shortlisted: "bg-primary",
        selected: "bg-success", rejected: "bg-danger",
      }[status] || "bg-secondary";
    }

    async function loadDrives() {
      const params = new URLSearchParams({ q: driveQuery.value, branch: branchFilter.value });
      drives.value = await api.get("/api/student/drives?" + params.toString());
    }
    async function loadApplications() {
      applications.value = await api.get("/api/student/applications");
    }
    async function loadProfile() {
      Object.assign(profile, await api.get("/api/student/profile"));
    }

    async function apply(driveId) {
      applyError.value = "";
      try {
        await api.post(`/api/student/drives/${driveId}/apply`);
        await loadApplications();
        await loadDrives();
      } catch (e) {
        applyError.value = e.message;
      }
    }

    async function saveProfile() {
      Object.assign(profile, await api.put("/api/student/profile", profile));
      profileMsg.value = "Profile saved.";
      setTimeout(() => profileMsg.value = "", 2000);
    }

    function onResumeSelected(e) {
      resumeFile.value = e.target.files[0] || null;
    }

    async function uploadResume() {
      if (!resumeFile.value) return;
      const formData = new FormData();
      formData.append("resume", resumeFile.value);
      try {
        const data = await api.upload("/api/student/resume", formData);
        profile.resume_filename = data.resume_filename;
        profileMsg.value = "Resume uploaded.";
      } catch (e) {
        profileMsg.value = e.message;
      }
      setTimeout(() => profileMsg.value = "", 2500);
    }

    async function exportCsv() {
      exportMsg.value = "Export started — you'll get an email/notification when it's ready.";
      try {
        await api.post("/api/student/export");
      } catch (e) {
        exportMsg.value = e.message;
      }
      setTimeout(() => exportMsg.value = "", 4000);
    }

    onMounted(async () => {
      await loadDrives();
      await loadApplications();
      await loadProfile();
    });

    return {
      tab, drives, driveQuery, branchFilter, applications, profile,
      applyError, profileMsg, exportMsg, resumeFile,
      badgeClass, loadDrives, apply, saveProfile, onResumeSelected, uploadResume, exportCsv,
    };
  },
  template: `
    <div class="container">
      <ul class="nav nav-tabs mb-3">
        <li class="nav-item"><a class="nav-link" :class="{active: tab==='drives'}" href="#" @click.prevent="tab='drives'">Available Drives</a></li>
        <li class="nav-item"><a class="nav-link" :class="{active: tab==='applications'}" href="#" @click.prevent="tab='applications'">My Applications</a></li>
        <li class="nav-item"><a class="nav-link" :class="{active: tab==='profile'}" href="#" @click.prevent="tab='profile'">Profile</a></li>
      </ul>

      <div v-if="tab==='drives'">
        <div class="d-flex mb-3 gap-2">
          <input v-model="driveQuery" @input="loadDrives" class="form-control" placeholder="Search job title...">
          <input v-model="branchFilter" @input="loadDrives" class="form-control" placeholder="Filter by branch...">
        </div>
        <div v-if="applyError" class="alert alert-danger py-2">{{ applyError }}</div>
        <div v-for="d in drives" :key="d.id" class="card p-3 mb-3">
          <div class="d-flex justify-content-between align-items-start">
            <div>
              <h6 class="mb-1">{{ d.job_title }} — <span class="text-muted">{{ d.company_name }}</span></h6>
              <p class="mb-1 small">{{ d.job_description }}</p>
              <small class="text-muted">
                Eligible: {{ d.eligible_branches || 'All branches' }} · Min CGPA: {{ d.min_cgpa }}
                · Deadline: {{ new Date(d.application_deadline).toLocaleString() }}
              </small>
            </div>
            <button class="btn btn-sm btn-primary" @click="apply(d.id)">Apply</button>
          </div>
        </div>
        <p v-if="drives.length===0" class="text-muted">No drives available right now.</p>
      </div>

      <div v-if="tab==='applications'">
        <button class="btn btn-outline-primary btn-sm mb-3" @click="exportCsv">Export Application History (CSV)</button>
        <span v-if="exportMsg" class="text-success ms-2">{{ exportMsg }}</span>
        <table class="table table-sm">
          <thead><tr><th>Company</th><th>Drive</th><th>Applied On</th><th>Status</th></tr></thead>
          <tbody>
            <tr v-for="a in applications" :key="a.id">
              <td>{{ a.company_name }}</td>
              <td>{{ a.job_title }}</td>
              <td>{{ new Date(a.application_date).toLocaleDateString() }}</td>
              <td><span class="badge" :class="badgeClass(a.status)">{{ a.status }}</span></td>
            </tr>
            <tr v-if="applications.length===0"><td colspan="4" class="text-muted">No applications yet.</td></tr>
          </tbody>
        </table>
      </div>

      <div v-if="tab==='profile'" class="card p-3" style="max-width:500px">
        <div v-if="profileMsg" class="alert alert-success py-2">{{ profileMsg }}</div>
        <form @submit.prevent="saveProfile">
          <div class="mb-2"><label class="form-label">Branch</label>
            <input v-model="profile.branch" class="form-control"></div>
          <div class="mb-2"><label class="form-label">Graduation Year</label>
            <input v-model.number="profile.year" type="number" class="form-control"></div>
          <div class="mb-3"><label class="form-label">CGPA</label>
            <input v-model.number="profile.cgpa" type="number" step="0.01" class="form-control"></div>
          <button class="btn btn-primary" type="submit">Save Profile</button>
        </form>
        <hr>
        <label class="form-label">Upload Resume (pdf/doc/docx)</label>
        <input type="file" class="form-control mb-2" @change="onResumeSelected">
        <button class="btn btn-outline-secondary btn-sm" @click="uploadResume" :disabled="!resumeFile">Upload Resume</button>
        <p class="small text-muted mt-2" v-if="profile.resume_filename">Current: {{ profile.resume_filename }}</p>
      </div>
    </div>
  `,
};
