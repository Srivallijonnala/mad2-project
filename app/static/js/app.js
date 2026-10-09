import { ref, computed, onMounted, watch } from "vue";
import { api } from "./api.js";
import { routerState, navigate, PUBLIC_PATHS, ROUTES } from "./router.js";

import Navbar from "./components/Navbar.js";
import Login from "./pages/Login.js";
import RegisterStudent from "./pages/RegisterStudent.js";
import RegisterCompany from "./pages/RegisterCompany.js";
import AdminDashboard from "./pages/AdminDashboard.js";
import CompanyDashboard from "./pages/CompanyDashboard.js";
import StudentDashboard from "./pages/StudentDashboard.js";
import NotFound from "./pages/NotFound.js";

export default {
  components: {
    Navbar, Login, RegisterStudent, RegisterCompany,
    AdminDashboard, CompanyDashboard, StudentDashboard, NotFound,
  },
  setup() {
    const user = ref(null);
    const ready = ref(false);

    function guard() {
      const path = routerState.path;
      if (user.value) {
      
        if (PUBLIC_PATHS.includes(path)) {
          navigate(`/${user.value.role}/dashboard`);
        }
      } else {
        
        if (!PUBLIC_PATHS.includes(path)) {
          navigate("/");
        }
      }
    }

    async function refreshUser() {
      try {
        user.value = await api.get("/api/auth/me");
      } catch (e) {
        user.value = null;
      } finally {
        ready.value = true;
        guard();
      }
    }

    onMounted(refreshUser);

    
    watch(() => routerState.path, () => { if (ready.value) guard(); });

    const currentComponent = computed(() => ROUTES[routerState.path] || "NotFound");

    return { user, ready, currentComponent, refreshUser, routerState };
  },

  template: `
    <div>
      <Navbar v-if="user" :user="user" @logout="refreshUser" />
      <component
        v-if="ready"
        :is="currentComponent"
        :key="routerState.path"
        @authed="refreshUser"
      />
    </div>
  `,
};
