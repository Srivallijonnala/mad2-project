import { reactive, ref } from "vue";
import { api } from "../api.js";
import { navigate } from "../router.js";

export default {
  setup() {
    const form = reactive({ name: "", email: "", password: "", company_name: "", hr_contact: "", website: "" });
    const error = ref("");
    const success = ref("");
    const loading = ref(false);

    async function submit() {
      error.value = ""; success.value = ""; loading.value = true;
      try {
        await api.post("/api/auth/register/company", form);
        success.value = "Registration submitted! Awaiting admin approval before you can log in.";
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
          <h4 class="mb-3">Company Registration</h4>
          <div v-if="error" class="alert alert-danger py-2">{{ error }}</div>
          <div v-if="success" class="alert alert-success py-2">{{ success }}</div>

          <form @submit.prevent="submit">
            <div class="mb-2"><label class="form-label">Your Name (HR / Contact person)</label>
              <input v-model="form.name" class="form-control" required></div>
            <div class="mb-2"><label class="form-label">Work Email</label>
              <input v-model="form.email" type="email" class="form-control" required></div>
            <div class="mb-2"><label class="form-label">Password</label>
              <input v-model="form.password" type="password" class="form-control" required></div>
            <div class="mb-2"><label class="form-label">Company Name</label>
              <input v-model="form.company_name" class="form-control" required></div>
            <div class="mb-2"><label class="form-label">HR Contact (phone)</label>
              <input v-model="form.hr_contact" class="form-control"></div>
            <div class="mb-3"><label class="form-label">Website</label>
              <input v-model="form.website" class="form-control" placeholder="https://"></div>
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
