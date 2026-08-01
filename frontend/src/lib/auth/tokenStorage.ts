// Plain storage helpers (not React state) so the Axios interceptor can
// read/write tokens synchronously outside any component. AuthContext
// mirrors this into React state for rendering.
//
// ASSUMPTION (flagged, not silently decided): tokens are kept in
// localStorage/sessionStorage, the standard pattern for an SPA talking to
// a pure JWT API with no cookie support specified in Architecture Freeze
// v1.0. An httpOnly-cookie-based refresh flow is more resistant to XSS
// token theft and worth considering as a hardening pass before real
// donations flow through this — noted here so it isn't lost.

const ACCESS_TOKEN_KEY = "grantloop_access_token";
const REFRESH_TOKEN_KEY = "grantloop_refresh_token";
const REMEMBER_ME_KEY = "grantloop_remember_me";

function storageFor(rememberMe: boolean): Storage {
  return rememberMe ? window.localStorage : window.sessionStorage;
}

function currentStorage(): Storage {
  const remembered = window.localStorage.getItem(REMEMBER_ME_KEY) === "true";
  return storageFor(remembered);
}

export const tokenStorage = {
  setTokens(accessToken: string, refreshToken: string, rememberMe: boolean): void {
    window.localStorage.setItem(REMEMBER_ME_KEY, String(rememberMe));
    const store = storageFor(rememberMe);
    store.setItem(ACCESS_TOKEN_KEY, accessToken);
    store.setItem(REFRESH_TOKEN_KEY, refreshToken);
  },

  setAccessToken(accessToken: string): void {
    currentStorage().setItem(ACCESS_TOKEN_KEY, accessToken);
  },

  getAccessToken(): string | null {
    return currentStorage().getItem(ACCESS_TOKEN_KEY);
  },

  getRefreshToken(): string | null {
    return currentStorage().getItem(REFRESH_TOKEN_KEY);
  },

  clear(): void {
    window.localStorage.removeItem(ACCESS_TOKEN_KEY);
    window.localStorage.removeItem(REFRESH_TOKEN_KEY);
    window.sessionStorage.removeItem(ACCESS_TOKEN_KEY);
    window.sessionStorage.removeItem(REFRESH_TOKEN_KEY);
    window.localStorage.removeItem(REMEMBER_ME_KEY);
  },
};
