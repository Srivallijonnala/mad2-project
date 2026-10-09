import { api } from "../api.js";
import { navigate } from "../router.js";

export default {
  props: { user: { type: Object, required: true } },
  emits: ["logout"],
  methods: {
    async doLogout() {
      await api.post("/api/auth/logout");
      this.$emit("logout");
      navigate("/");
    },
  },
  template: `
    <nav class="navbar navbar-dark bg-primary mb-4">
      <div class="container">
        <span class="navbar-brand">Placement Portal — {{ user.role.charAt(0).toUpperCase() + user.role.slice(1) }}</span>
        <span class="text-light small me-3">{{ user.name }}</span>
        <button class="btn btn-outline-light btn-sm" @click="doLogout">Logout</button>
      </div>
    </nav>
  `,
};
