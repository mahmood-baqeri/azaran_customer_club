import { DOMAIN } from "../constants/env";



export const handel_photo_address = (i: string | null | undefined) => i ? (i.startsWith("http") ? i : `${DOMAIN}${i}`) : undefined;