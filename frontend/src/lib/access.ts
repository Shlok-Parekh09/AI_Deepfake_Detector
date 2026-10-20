/** Missing Firebase configuration must never grant hosted-site access. */
export function isLocalhost(hostname: string): boolean {
  return ['localhost','127.0.0.1','[::1]','::1'].includes(hostname.toLowerCase());
}
export const localDevelopmentBypass = import.meta.env.DEV && isLocalhost(window.location.hostname);
