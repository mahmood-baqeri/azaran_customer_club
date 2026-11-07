// src/types/global.d.ts
export {};

interface OwlCarouselOptions {
  items?: number;
  margin?: number;
  loop?: boolean;
  center?: boolean;
  autoplay?: boolean;
  autoplayTimeout?: number;
  autoplayHoverPause?: boolean;
  nav?: boolean;
  dots?: boolean;
  smartSpeed?: number;
  responsive?: Record<number, OwlCarouselOptions>;
  [key: string]: unknown;
}

declare global {
  interface JQuery {
    owlCarousel(options?: OwlCarouselOptions): JQuery;
    owlCarousel(
      command: "next" | "prev" | "to" | "destroy" | "refresh" | "play" | "stop",
      arg?: number | string | boolean
    ): JQuery;
  }

  interface Window {
    Eggy: (options: {
      title: string;
      message: string;
      position?: string;
      type?: "success" | "error" | "info" | "warning";
      duration?: number;
    }) => void;
  }
}