//  src/shared/utils/notification.ts

export function MyNotification(
  title: string,
  msg: string,
  type: "success" | "error" | "info" | "warning"
) {
  if (typeof window !== "undefined" && window.Eggy) {
    window.Eggy({
      title,
      message: msg,
      position: "top-left",
      type,
      duration: 8000,
    });
  } else {
    console.warn("Eggy is not loaded!");
  }
}