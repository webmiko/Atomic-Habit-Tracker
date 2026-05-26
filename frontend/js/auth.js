/** JWT: вход, регистрация, refresh и выход. */
const Auth = {
  getAccess() {
    return localStorage.getItem("access");
  },

  getRefresh() {
    return localStorage.getItem("refresh");
  },

  saveTokens(access, refresh) {
    localStorage.setItem("access", access);
    localStorage.setItem("refresh", refresh);
  },

  clearTokens() {
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
  },

  isLoggedIn() {
    return Boolean(this.getAccess());
  },

  logout() {
    this.clearTokens();
    window.location.href = "login.html";
  },

  async tryRefresh() {
    const refresh = this.getRefresh();
    if (!refresh) {
      return false;
    }
    const base = Api.getBaseUrl();
    const response = await fetch(`${base}/api/token/refresh/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh }),
    });
    if (!response.ok) {
      return false;
    }
    const data = await response.json();
    this.saveTokens(data.access, refresh);
    return true;
  },

  async register(email, password) {
    const response = await Api.request("/api/users/register/", {
      method: "POST",
      body: JSON.stringify({ email, password }),
      skipAuth: true,
    });
    if (!response.ok) {
      const err = await Api.parseError(response);
      throw new Error(err);
    }
  },

  async login(email, password) {
    const response = await Api.request("/api/token/", {
      method: "POST",
      body: JSON.stringify({ email, password }),
      skipAuth: true,
    });
    if (!response.ok) {
      const err = await Api.parseError(response);
      throw new Error(err);
    }
    const data = await response.json();
    this.saveTokens(data.access, data.refresh);
  },

  requireAuth() {
    if (!this.isLoggedIn()) {
      window.location.href = "login.html";
    }
  },
};
