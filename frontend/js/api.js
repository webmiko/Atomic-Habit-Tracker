/** HTTP-клиент к Django API с JWT. */
const Api = {
  getBaseUrl() {
    return localStorage.getItem("api_base_url") || API_BASE_URL;
  },

  async parseError(response) {
    try {
      const data = await response.json();
      if (typeof data === "object" && data !== null) {
        const parts = [];
        for (const [key, value] of Object.entries(data)) {
          if (Array.isArray(value)) {
            parts.push(`${key}: ${value.join(", ")}`);
          } else if (typeof value === "string") {
            parts.push(value);
          }
        }
        if (parts.length) {
          return parts.join("; ");
        }
      }
      return JSON.stringify(data);
    } catch {
      return `Ошибка ${response.status}`;
    }
  },

  async request(path, options = {}) {
    const headers = {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    };
    if (!options.skipAuth) {
      const token = Auth.getAccess();
      if (token) {
        headers.Authorization = `Bearer ${token}`;
      }
    }
    const response = await fetch(`${this.getBaseUrl()}${path}`, {
      ...options,
      headers,
    });
    if (response.status === 401 && !options.skipAuth && !options._retry) {
      const refreshed = await Auth.tryRefresh();
      if (refreshed) {
        return this.request(path, { ...options, _retry: true });
      }
      Auth.logout();
      throw new Error("Сессия истекла");
    }
    return response;
  },

  async json(path, options = {}) {
    const response = await this.request(path, options);
    if (!response.ok) {
      throw new Error(await this.parseError(response));
    }
    if (response.status === 204) {
      return null;
    }
    return response.json();
  },
};
