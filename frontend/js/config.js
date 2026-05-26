/** Базовый URL API: тот же хост при деплое, иначе localhost:8000. */
const API_BASE_URL = window.location.origin.includes("5500")
  ? "http://127.0.0.1:8000"
  : window.location.origin;
