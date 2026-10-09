import { ref, reactive, onMounted } from "vue";
import { api } from "../api.js";

export default {
  setup() {
    const tab = ref("drives");
    const profile = ref(null);
    const drives = ref([]);
    const selectedDriveId = ref(null);
    const applications = ref([]);
    const form = reactive({
      job_title: "", job_description: "", eligible_branches: "",
      min_cgpa: 0, eligible_year: null, application_deadline: "",
    });
    const createError = ref("");
    const createSuccess = ref("");
    const loading = ref(false);

    function badgeClass(status) {
      return {
        approved: "bg-success", pending: "bg-warning text-dark", rejected: "bg-danger",
        closed: "bg-secondary", applied: "bg-info text-dark", shortlisted: "bg-primary",
        selected: "bg-success",
      }[status] || "bg-secondary";
    }

    async function loadDrives() {
      drives.value = await api.get("/api/company/drives");
    }

    async function viewApplications(driveId) {
      if (selectedDriveId.value === driveId) { selectedDriveId.value = null; return; }
      selectedDriveId.value = driveId;
      applications.value = await api.get(`/api/company/drives/${driveId}/applications`);
    }

    async function updateStatus(applicationId, status) {
      if (!status) return;
      await api.put(`/api/company/applications/${applicationId}/status`, { status });
      applications.value = await api.get(`/api/company/drives/${selectedDriveId.value}/applications`);
      await loadDrives();
    }

    async function createDrive() {
      createError.value = ""; createSuccess.value = ""; loading.value = true;
      try {
        const payload = { ...form };
        payload.application_deadline = new Date(form.application_deadline).toISOString();
        await api.post("/api/company/drives", payload);
        createSuccess.value = "Drive submitted for admin approval.";
        Object.assign(form, { job_title: "", job_description: "", eligible_branches: "", min_cgpa: 0, eligible_year: null, application_deadline: "" });
        await loadDrives();
      } catch (e) {
        createError.value = e.message;
      } finally {
        loading.value = false;
      }
    }

    onMounted(async () => {
      profile.value = await api.get("/api/company/profile");
      await loadDrives();
    });

    return {
      tab, profile, drives, selectedDriveId, applications, form,
      createError, createSuccess, loading,
      badgeClass, viewApplications, updateStatus, createDrive,
    };
  },
  template: `
    <div class="container">
      <div class="card p-3 mb-4" v-if="profile">
        <h5>{{ profile.company_name }}
          <span class="badge" :class="profile.approval_status==='approved' ? 'bg-success' : 'bg-warning text-dark'">
            {{ profile.approval_status }}
          </span>
        </h5>
        <p class="text-muted mb-0">HR Contact: {{ profile.hr_contact || '—' }} | Website: {{ profile.website || '—' }}</p>
      </div>

      <ul class="nav nav-tabs mb-3">
        <li class="nav-item"><a class="nav-link" :class="{active: tab==='drives'}" href="#" @click.prevent="tab='drives'">My Drives</a></li>
        <li class="nav-item"><a class="nav-link" :class="{active: tab==='create'}" href="#" @click.prevent="tab='create'">Create Drive</a></li>
      </ul>

      <div v-if="tab==='drives'">
        <div v-for="d in drives" :key="d.id" class="card p-3 mb-3">
          <div class="d-flex justify-content-between">
            <div>
              <h6 class="mb-0">{{ d.job_title }}
                <span class="badge" :class="badgeClass(d.status)">{{ d.status }}</span>
              </h6>
              <small class="text-muted">Deadline: {{ new Date(d.application_deadline).toLocaleString() }} · {{ d.applicant_count }} applicants</small>
            </div>
            <button class="btn btn-sm btn-primary" @click="viewApplications(d.id)">View Applications</button>
          </div>

          <div v-if="selectedDriveId===d.id" class="mt-3">
            <table class="table table-sm">
              <thead><tr><th>Student</th><th>Branch</th><th>CGPA</th><th>Status</th><th>Update</th></tr></thead>
              <tbody>
                <tr v-for="a in applications" :key="a.id">
                  <td>{{ a.student_name }} <br><small class="text-muted">{{ a.student_email }}</small></td>
                  <td>{{ a.branch }}</td>
                  <td>{{ a.cgpa }}</td>
                  <td><span class="badge" :class="badgeClass(a.status)">{{ a.status }}</span></td>
                  <td>
                    <select class="form-select form-select-sm" @change="updateStatus(a.id, $event.target.value)">
                      <option disabled selected value="">Change...</option>
                      <option value="shortlisted">Shortlist</option>
                      <option value="selected">Select</option>
                      <option value="rejected">Reject</option>
                    </select>
                  </td>
                </tr>
                <tr v-if="applications.length===0"><td colspan="5" class="text-muted">No applications yet.</td></tr>
              </tbody>
            </table>
          </div>
        </div>
        <p v-if="drives.length===0" class="text-muted">No drives created yet.</p>
      </div>

      <div v-if="tab==='create'" class="card p-3" style="max-width:600px">
        <div v-if="createError" class="alert alert-danger py-2">{{ createError }}</div>
        <div v-if="createSuccess" class="alert alert-success py-2">{{ createSuccess }}</div>
        <form @submit.prevent="createDrive">
          <div class="mb-2"><label class="form-label">Job Title</label>
            <input v-model="form.job_title" class="form-control" required></div>
          <div class="mb-2"><label class="form-label">Job Description</label>
            <textarea v-model="form.job_description" class="form-control" rows="3"></textarea></div>
          <div class="row">
            <div class="col mb-2"><label class="form-label">Eligible Branches (comma separated)</label>
              <input v-model="form.eligible_branches" class="form-control" placeholder="CSE,ECE"></div>
            <div class="col mb-2"><label class="form-label">Min CGPA</label>
              <input v-model.number="form.min_cgpa" type="number" step="0.1" class="form-control"></div>
          </div>
          <div class="row">
            <div class="col mb-2"><label class="form-label">Eligible Graduation Year</label>
              <input v-model.number="form.eligible_year" type="number" class="form-control" placeholder="2026"></div>
            <div class="col mb-3"><label class="form-label">Application Deadline</label>
              <input v-model="form.application_deadline" type="datetime-local" class="form-control" required></div>
          </div>
          <button class="btn btn-primary" :disabled="loading">{{ loading ? "Submitting..." : "Submit for Approval" }}</button>
        </form>
      </div>
    </div>
  `,
};
