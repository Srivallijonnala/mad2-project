import { reactive, ref } from "vue";
import { api } from "../api.js";
import { navigate } from "../router.js";

export default {
  setup() {
    const form = reactive({ name: "", email: "", password: "", branch: "", year: null, cgpa: null });
    const error = ref("");
    const success = ref("");
    const loading = ref(false);

    async function submit() {
      error.value = ""; success.value = ""; loading.value = true;
      try {
        await api.post("/api/auth/register/student", form);
        success.value = "Registration successful! Redirecting to login...";
        setTimeout(() => navigate("/"), 1200);
      } catch (e) {
        error.value = e.message;
      } finally {
        loading.value = false;
      }
    }

    return { form, error, success, loading, submit, goLogin: () => navigate("/") };
  },
  template: `
    <div class="container d-flex align-items-center justify-content-center" style="min-height:100vh">
      <div style="width:100%; max-width:480px">
        <div class="card p-4">
          <h4 class="mb-3">Student Registration</h4>
          <div v-if="error" class="alert alert-danger py-2">{{ error }}</div>
          <div v-if="success" class="alert alert-success py-2">{{ success }}</div>

          <form @submit.prevent="submit">
            <div class="mb-2"><label class="form-label">Full Name</label>
              <input v-model="form.name" class="form-control" required></div>
            <div class="mb-2"><label class="form-label">Email</label>
              <input v-model="form.email" type="email" class="form-control" required></div>
            <div class="mb-2"><label class="form-label">Password</label>
              <input v-model="form.password" type="password" class="form-control" required></div>
            <div class="row">
              <div class="col mb-2"><label class="form-label">Branch</label>
                <input v-model="form.branch" class="form-control" placeholder="CSE"></div>
              <div class="col mb-2"><label class="form-label">Graduation Year</label>
                <input v-model.number="form.year" type="number" class="form-control" placeholder="2026"></div>
            </div>
            <div class="mb-3"><label class="form-label">CGPA</label>
              <input v-model.number="form.cgpa" type="number" step="0.01" class="form-control"></div>
            <button class="btn btn-primary w-100" :disabled="loading">
              {{ loading ? "Submitting..." : "Register" }}
            </button>
          </form>
          <p class="text-center mt-3 mb-0"><a href="#" @click.prevent="goLogin">Back to login</a></p>
        </div>
      </div>
    </div>
  `,
};
