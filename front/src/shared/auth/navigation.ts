//  src/shared/auth/navigation.ts

let navigator: ((to: string) => void) | null = null;

export const setNavigator = (nav: (to: string) => void): void => {
  navigator = nav;
};

export const redirectTo = (to: string): void => {
  if (navigator) navigator(to);
  else console.error("[navigation] Navigator is not set");
};