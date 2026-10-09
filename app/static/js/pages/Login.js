import { ref } from "vue";
import { api } from "../api.js";
import { navigate } from "../router.js";

export default {
  emits: ["authed"],
  setup(props, { emit }) {
    const email = ref("");
    const password = ref("");
    const error = ref("");
    const loading = ref(false);

    async function login() {
      error.value = "";
      loading.value = true;
      try {
        const data = await api.post("/api/auth/login", { email: email.value, password: password.value });
        emit("authed");
        navigate(`/${data.user.role}/dashboard`);
      } catch (e) {
        error.value = e.message;
      } finally {
        loading.value = false;
      }
    }

    return {
      email, password, error, loading, login,
      goRegisterStudent: () => navigate("/register/student"),
      goRegisterCompany: () => navigate("/register/company"),
    };
  },
  template: `
    <div class="container d-flex align-items-center justify-content-center" style="min-height:100vh">
      <div style="width:100%; max-width:420px">
        <div class="card p-4">
          <h3 class="mb-1 text-center">Placement Portal</h3>
          <p class="text-muted text-center mb-4">Sign in to continue</p>

          <div v-if="error" class="alert alert-danger py-2">{{ error }}</div>

          <form @submit.prevent="login">
            <div class="mb-3">
              <label class="form-label">Email</label>
              <input v-model="email" type="email" class="form-control" required>
            </div>
            <div class="mb-3">
              <label class="form-label">Password</label>
              <input v-model="password" type="password" class="form-control" required>
            </div>
            <button class="btn btn-primary w-100" type="submit" :disabled="loading">
              {{ loading ? "Signing in..." : "Login" }}
            </button>
          </form>

          <hr>
          <p class="text-center mb-1">New here?</p>
          <div class="d-grid gap-2">
            <button class="btn btn-outline-secondary btn-sm" @click="goRegisterStudent">Register as Student</button>
            <button class="btn btn-outline-secondary btn-sm" @click="goRegisterCompany">Register as Company</button>
          </div>
        </div>
      </div>
    </div>
  `,
};
