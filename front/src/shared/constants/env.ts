//  src/shared/constants/env.ts

export const APPLEVEL = "1.1.1";
export const DOMAIN = "http://127.0.0.1:8000";
export const Domain_Manager = "http://127.0.0.1:8000/manager";

const LOCAL_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0", "::1"];
export const RunInServer = !LOCAL_HOSTS.includes(window.location.hostname);

export const MEDIA = `${DOMAIN}/media/`;
export const BASE_URL = `${Domain_Manager}/api/v1/`;