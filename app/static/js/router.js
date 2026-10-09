import { reactive } from "vue";
export const routerState = reactive({ path: window.location.pathname });

window.addEventListener("popstate", () => {
  routerState.path = window.location.pathname;
});


export function navigate(path) {
  if (path !== routerState.path) {
    window.history.pushState({}, "", path);
  }
  routerState.path = path;
}

export const PUBLIC_PATHS = ["/", "/register/student", "/register/company"];

export const ROUTES = {
  "/": "Login",
  "/register/student": "RegisterStudent",
  "/register/company": "RegisterCompany",
  "/admin/dashboard": "AdminDashboard",
  "/company/dashboard": "CompanyDashboard",
  "/student/dashboard": "StudentDashboard",
};
