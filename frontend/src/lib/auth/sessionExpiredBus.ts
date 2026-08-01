type Listener = () => void;

let listener: Listener | null = null;

/** AuthProvider registers itself here once, on mount. The Axios
 * interceptor calls this when a refresh attempt fails, so a truly
 * expired session forces logout + redirect without lib/api needing to
 * import React context (which would create a circular dependency, since
 * AuthContext itself depends on the Axios client). */
export const sessionExpiredBus = {
  subscribe(fn: Listener): void {
    listener = fn;
  },
  emit(): void {
    listener?.();
  },
};
