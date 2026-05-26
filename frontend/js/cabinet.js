/** Кабинет: вкладки Мои / Сообщество / Каталог / Настройки. */
const Cabinet = {
  myNext: null,
  communityNext: null,
  templatesNext: null,
  selectedPublicId: null,
  habitModal: null,
  publicModal: null,

  init() {
    Auth.requireAuth();
    this.habitModal = new bootstrap.Modal(document.getElementById("habit-modal"));
    this.publicModal = new bootstrap.Modal(document.getElementById("public-modal"));
    document.getElementById("btn-logout").addEventListener("click", () => Auth.logout());
    document.getElementById("btn-add-habit").addEventListener("click", () => this.openHabitModal());
    document.getElementById("habit-form").addEventListener("submit", (e) => this.saveHabit(e));
    document.getElementById("habit-pleasant").addEventListener("change", () => this.toggleRewardFields());
    document.getElementById("settings-form").addEventListener("submit", (e) => this.saveSettings(e));
    document.getElementById("btn-tg-code").addEventListener("click", () => this.requestTelegramCode());
    document.getElementById("btn-copy-public").addEventListener("click", () => this.copyPublicHabit());
    document.querySelectorAll("[data-section]").forEach((link) => {
      link.addEventListener("click", (e) => {
        e.preventDefault();
        window.location.hash = link.getAttribute("data-section");
      });
    });
    window.addEventListener("hashchange", () => this.route());
    this.route();
  },

  showError(message) {
    const el = document.getElementById("global-alert");
    el.textContent = message;
    el.classList.remove("alert-success");
    el.classList.add("alert-danger");
    el.classList.remove("d-none");
    setTimeout(() => el.classList.add("d-none"), 5000);
  },

  showSuccess(message) {
    const el = document.getElementById("global-alert");
    el.textContent = message;
    el.classList.remove("alert-danger");
    el.classList.add("alert-success");
    el.classList.remove("d-none");
    setTimeout(() => el.classList.add("d-none"), 4000);
  },

  pathFromNext(next) {
    if (!next) {
      return null;
    }
    const url = new URL(next);
    return `${url.pathname}${url.search}`;
  },

  formatTime(value) {
    if (!value) {
      return "";
    }
    return String(value).slice(0, 5);
  },

  badgeHtml(isPleasant) {
    return isPleasant
      ? '<span class="badge badge-pleasant">приятная</span>'
      : '<span class="badge badge-useful">полезная</span>';
  },

  renderPagination(containerId, data, onLoad) {
    const nav = document.getElementById(containerId);
    nav.innerHTML = "";
    if (!data || data.count <= data.results.length) {
      return;
    }
    const ul = document.createElement("ul");
    ul.className = "pagination pagination-sm mb-0";
    if (data.previous) {
      const li = document.createElement("li");
      li.className = "page-item";
      li.innerHTML = '<a class="page-link" href="#">Назад</a>';
      li.querySelector("a").addEventListener("click", (e) => {
        e.preventDefault();
        onLoad(Cabinet.pathFromNext(data.previous));
      });
      ul.appendChild(li);
    }
    if (data.next) {
      const li = document.createElement("li");
      li.className = "page-item";
      li.innerHTML = '<a class="page-link" href="#">Далее</a>';
      li.querySelector("a").addEventListener("click", (e) => {
        e.preventDefault();
        onLoad(Cabinet.pathFromNext(data.next));
      });
      ul.appendChild(li);
    }
    nav.appendChild(ul);
  },

  setActiveNav(section) {
    document.querySelectorAll("[data-section]").forEach((link) => {
      link.classList.toggle("active", link.getAttribute("data-section") === section);
    });
    document.querySelectorAll(".section-panel").forEach((panel) => {
      panel.classList.remove("active");
    });
    const panel = document.getElementById(`panel-${section}`);
    if (panel) {
      panel.classList.add("active");
    }
  },

  route() {
    const section = window.location.hash.replace("#", "") || "my";
    this.setActiveNav(section);
    if (section === "my") {
      this.loadMyHabits("/api/habits/");
    } else if (section === "community") {
      this.loadCommunity("/api/habits/public/");
    } else if (section === "templates") {
      this.loadTemplates("/api/habits/templates/");
    } else if (section === "settings") {
      this.loadSettings();
    }
  },

  async loadMyHabits(path) {
    try {
      const data = await Api.json(path);
      const list = document.getElementById("my-list");
      list.innerHTML = "";
      if (!data.results.length) {
        list.innerHTML = '<p class="form-hint">Пока нет привычек. Добавьте первую.</p>';
      }
      data.results.forEach((habit) => {
        const col = document.createElement("div");
        col.className = "col-12 col-md-6";
        col.innerHTML = `
          <div class="card habit-card h-100">
            <div class="card-body">
              <div class="d-flex justify-content-between">
                <h3 class="h6">${habit.action}</h3>
                ${this.badgeHtml(habit.is_pleasant)}
              </div>
              <p class="mb-1 small">${habit.place} · ${this.formatTime(habit.time)}</p>
              <p class="mb-2 small text-muted">
                ${habit.duration} сек · каждые ${habit.periodicity} дн.
                ${habit.is_public ? " · публичная" : ""}
              </p>
              <div class="btn-group btn-group-sm">
                <button type="button" class="btn btn-outline-secondary btn-edit">Изменить</button>
                <button type="button" class="btn btn-outline-danger btn-del">Удалить</button>
              </div>
            </div>
          </div>`;
        col.querySelector(".btn-edit").addEventListener("click", () => this.openHabitModal(habit));
        col.querySelector(".btn-del").addEventListener("click", () => this.deleteHabit(habit.id));
        list.appendChild(col);
      });
      this.renderPagination("my-pagination", data, (p) => this.loadMyHabits(p));
    } catch (error) {
      this.showError(error.message);
    }
  },

  async loadPleasantOptions(selectedId) {
    const select = document.getElementById("habit-related");
    select.innerHTML = '<option value="">—</option>';
    let path = "/api/habits/";
    const pleasant = [];
    while (path) {
      const data = await Api.json(path);
      data.results.filter((h) => h.is_pleasant).forEach((h) => pleasant.push(h));
      path = this.pathFromNext(data.next);
    }
    pleasant.forEach((h) => {
      const opt = document.createElement("option");
      opt.value = h.id;
      opt.textContent = h.action;
      if (selectedId && Number(selectedId) === h.id) {
        opt.selected = true;
      }
      select.appendChild(opt);
    });
  },

  toggleRewardFields() {
    const isPleasant = document.getElementById("habit-pleasant").value === "true";
    document.getElementById("reward-group").classList.toggle("d-none", isPleasant);
    document.getElementById("related-group").classList.toggle("d-none", isPleasant);
  },

  async openHabitModal(habit) {
    document.getElementById("habit-modal-title").textContent = habit ? "Изменить" : "Новая привычка";
    document.getElementById("habit-id").value = habit ? habit.id : "";
    document.getElementById("habit-action").value = habit ? habit.action : "";
    document.getElementById("habit-place").value = habit ? habit.place : "";
    document.getElementById("habit-time").value = habit ? this.formatTime(habit.time) : "08:00";
    document.getElementById("habit-duration").value = habit ? habit.duration : 60;
    document.getElementById("habit-periodicity").value = habit ? habit.periodicity : 1;
    document.getElementById("habit-pleasant").value = habit ? String(habit.is_pleasant) : "false";
    document.getElementById("habit-reward").value = habit ? habit.reward || "" : "";
    document.getElementById("habit-public").checked = habit ? habit.is_public : false;
    await this.loadPleasantOptions(habit ? habit.related_habit : null);
    this.toggleRewardFields();
    this.habitModal.show();
  },

  buildHabitPayload() {
    const isPleasant = document.getElementById("habit-pleasant").value === "true";
    const related = document.getElementById("habit-related").value;
    const payload = {
      place: document.getElementById("habit-place").value.trim(),
      time: `${document.getElementById("habit-time").value}:00`,
      action: document.getElementById("habit-action").value.trim(),
      is_pleasant: isPleasant,
      periodicity: Number(document.getElementById("habit-periodicity").value),
      duration: Number(document.getElementById("habit-duration").value),
      is_public: document.getElementById("habit-public").checked,
      reward: "",
      related_habit: null,
    };
    if (!isPleasant) {
      payload.reward = document.getElementById("habit-reward").value.trim();
      if (related) {
        payload.related_habit = Number(related);
        payload.reward = "";
      }
    }
    return payload;
  },

  async saveHabit(event) {
    event.preventDefault();
    const id = document.getElementById("habit-id").value;
    const payload = this.buildHabitPayload();
    try {
      if (id) {
        await Api.json(`/api/habits/${id}/`, {
          method: "PATCH",
          body: JSON.stringify(payload),
        });
      } else {
        await Api.json("/api/habits/", {
          method: "POST",
          body: JSON.stringify(payload),
        });
      }
      this.habitModal.hide();
      this.loadMyHabits("/api/habits/");
    } catch (error) {
      this.showError(error.message);
    }
  },

  async deleteHabit(id) {
    if (!window.confirm("Удалить привычку?")) {
      return;
    }
    try {
      await Api.json(`/api/habits/${id}/`, { method: "DELETE" });
      this.loadMyHabits("/api/habits/");
    } catch (error) {
      this.showError(error.message);
    }
  },

  async loadCommunity(path) {
    try {
      const data = await Api.json(path);
      const list = document.getElementById("community-list");
      list.innerHTML = "";
      if (!data.results.length) {
        list.innerHTML = '<p class="form-hint">Пока нет чужих публичных привычек.</p>';
      }
      data.results.forEach((habit) => {
        const col = document.createElement("div");
        col.className = "col-12 col-md-6";
        col.innerHTML = `
          <div class="card habit-card h-100">
            <div class="card-body">
              <div class="d-flex justify-content-between">
                <h3 class="h6">${habit.action}</h3>
                ${this.badgeHtml(habit.is_pleasant)}
              </div>
              <p class="mb-1 small">${habit.author_name}</p>
              <p class="mb-2 small text-muted">${habit.formula}</p>
              <button type="button" class="btn btn-outline-success btn-sm btn-open">Подробнее</button>
            </div>
          </div>`;
        col.querySelector(".btn-open").addEventListener("click", () => this.openPublicModal(habit));
        list.appendChild(col);
      });
      this.renderPagination("community-pagination", data, (p) => this.loadCommunity(p));
    } catch (error) {
      this.showError(error.message);
    }
  },

  openPublicModal(habit) {
    this.selectedPublicId = habit.id;
    const body = document.getElementById("public-modal-body");
    let reward = "";
    if (habit.related_action) {
      reward = `<p><strong>Связь:</strong> ${habit.related_action}</p>`;
    } else if (habit.reward) {
      reward = `<p><strong>Награда:</strong> ${habit.reward}</p>`;
    }
    body.innerHTML = `
      <p>${habit.formula}</p>
      <p class="small text-muted">Автор: ${habit.author_name}</p>
      <p class="small">${habit.place} · ${this.formatTime(habit.time)} · ${habit.duration} сек</p>
      ${reward}`;
    this.publicModal.show();
  },

  async copyPublicHabit() {
    if (!this.selectedPublicId) {
      return;
    }
    try {
      await Api.json(`/api/habits/public/${this.selectedPublicId}/copy/`, { method: "POST" });
      this.publicModal.hide();
      window.location.hash = "my";
      this.showSuccess("Привычка добавлена в «Мои»");
    } catch (error) {
      this.showError(error.message);
    }
  },

  async loadTemplates(path) {
    try {
      const data = await Api.json(path);
      const list = document.getElementById("templates-list");
      list.innerHTML = "";
      data.results.forEach((tpl) => {
        const col = document.createElement("div");
        col.className = "col-12 col-md-6";
        const featured = tpl.is_featured ? '<span class="badge bg-warning text-dark">топ</span>' : "";
        col.innerHTML = `
          <div class="card habit-card h-100">
            <div class="card-body">
              <div class="d-flex justify-content-between gap-2">
                <h3 class="h6">${tpl.action}</h3>
                <div>${featured} ${this.badgeHtml(tpl.is_pleasant)}</div>
              </div>
              <p class="small text-muted mb-1">${tpl.tagline || tpl.category}</p>
              <p class="small mb-2">${tpl.place} · ${this.formatTime(tpl.time)}</p>
              <button type="button" class="btn btn-success btn-sm btn-add-tpl">Добавить к себе</button>
            </div>
          </div>`;
        col.querySelector(".btn-add-tpl").addEventListener("click", () => this.addFromTemplate(tpl.id));
        list.appendChild(col);
      });
      this.renderPagination("templates-pagination", data, (p) => this.loadTemplates(p));
    } catch (error) {
      this.showError(error.message);
    }
  },

  async addFromTemplate(id) {
    try {
      await Api.json(`/api/habits/from-template/${id}/`, { method: "POST" });
      window.location.hash = "my";
      this.showSuccess("Шаблон добавлен в «Мои»");
    } catch (error) {
      this.showError(error.message);
    }
  },

  async loadSettings() {
    try {
      const profile = await Api.json("/api/users/me/");
      document.getElementById("settings-email").value = profile.email;
      document.getElementById("settings-name").value = profile.public_display_name || "";
      document.getElementById("settings-email-notify").checked = profile.notify_by_email;
      document.getElementById("settings-tg-notify").checked = profile.notify_by_telegram;
      document.getElementById("tg-status").textContent = profile.telegram_linked
        ? "привязан"
        : "не привязан";
    } catch (error) {
      this.showError(error.message);
    }
  },

  async saveSettings(event) {
    event.preventDefault();
    try {
      await Api.json("/api/users/me/", {
        method: "PATCH",
        body: JSON.stringify({
          public_display_name: document.getElementById("settings-name").value.trim(),
          notify_by_email: document.getElementById("settings-email-notify").checked,
          notify_by_telegram: document.getElementById("settings-tg-notify").checked,
        }),
      });
      await this.loadSettings();
    } catch (error) {
      this.showError(error.message);
    }
  },

  async requestTelegramCode() {
    try {
      const data = await Api.json("/api/users/telegram/link/", { method: "POST" });
      document.getElementById("tg-code-box").classList.remove("d-none");
      document.getElementById("tg-code-text").textContent = `/link ${data.code}`;
      document.getElementById("tg-code-expires").textContent =
        `Код действует ${data.expires_in_minutes} мин.`;
    } catch (error) {
      this.showError(error.message);
    }
  },
};

document.addEventListener("DOMContentLoaded", () => Cabinet.init());
