// src/shared/components/AuthIcons.tsx

interface IconProps {
     size?: number;
     className?: string;
     style?: React.CSSProperties;
}

const base = (size: number) => ({
     width: size,
     height: size,
     viewBox: "0 0 24 24",
     fill: "none",
     stroke: "currentColor",
     strokeWidth: 1.8,
     strokeLinecap: "round" as const,
     strokeLinejoin: "round" as const,
});

export const IconSmartphone = ({ size = 20, ...p }: IconProps) => (
     <svg {...base(size)} {...p}>
          <rect x="6" y="2" width="12" height="20" rx="3" />
          <circle cx="12" cy="18" r="0.5" fill="currentColor" />
     </svg>
);

export const IconShieldCheck = ({ size = 20, ...p }: IconProps) => (
     <svg {...base(size)} {...p}>
          <path d="M12 2 4 6v6c0 5 3.5 9 8 10 4.5-1 8-5 8-10V6l-8-4Z" />
          <path d="m8.5 12 2.5 2.5 4.5-5" />
     </svg>
);

export const IconMail = ({ size = 20, ...p }: IconProps) => (
     <svg {...base(size)} {...p}>
          <rect x="2.5" y="5" width="19" height="14" rx="2.5" />
          <path d="m3 7 9 6 9-6" />
     </svg>
);

export const IconKey = ({ size = 20, ...p }: IconProps) => (
     <svg {...base(size)} {...p}>
          <circle cx="8" cy="15" r="4" />
          <path d="m10.8 12.2 8.2-8.2M16 5l3 3M14 7l2 2" />
     </svg>
);

export const IconLock = ({ size = 20, ...p }: IconProps) => (
     <svg {...base(size)} {...p}>
          <rect x="4" y="10.5" width="16" height="10.5" rx="2.5" />
          <path d="M8 10.5V7a4 4 0 0 1 8 0v3.5" />
     </svg>
);

export const IconEye = ({ size = 20, ...p }: IconProps) => (
     <svg {...base(size)} {...p}>
          <path d="M1.5 12S5 5 12 5s10.5 7 10.5 7-3.5 7-10.5 7S1.5 12 1.5 12Z" />
          <circle cx="12" cy="12" r="3" />
     </svg>
);

export const IconEyeOff = ({ size = 20, ...p }: IconProps) => (
     <svg {...base(size)} {...p}>
          <path d="M3 3l18 18" />
          <path d="M10.6 5.2A10 10 0 0 1 12 5c7 0 10.5 7 10.5 7a17.6 17.6 0 0 1-3.9 4.6" />
          <path d="M6.6 6.6C3.6 8.4 1.5 12 1.5 12S5 19 12 19c1.7 0 3.2-.4 4.6-1" />
          <path d="M9.9 9.9a3 3 0 0 0 4.2 4.2" />
     </svg>
);

export const IconLoader = ({ size = 20, className = "", ...p }: IconProps) => (
     <svg
          {...base(size)}
          className={`auth-spin ${className}`}
          {...p}
     >
          <path d="M21 12a9 9 0 1 1-6.2-8.5" />
     </svg>
);

export const IconArrowLeft = ({ size = 18, ...p }: IconProps) => (
     <svg {...base(size)} {...p}>
          <path d="M19 12H5M12 19l-7-7 7-7" />
     </svg>
);

export const IconArrowRight = ({ size = 18, ...p }: IconProps) => (
     <svg {...base(size)} {...p}>
          <path d="M5 12h14M12 5l7 7-7 7" />
     </svg>
);

export const IconUser = ({ size = 20, ...p }: IconProps) => (
     <svg {...base(size)} {...p}>
          <circle cx="12" cy="8" r="4" />
          <path d="M4 21c0-4.4 3.6-8 8-8s8 3.6 8 8" />
     </svg>
);

export const IconStore = ({ size = 20, ...p }: IconProps) => (
     <svg {...base(size)} {...p}>
          <path d="M3 9h18l-1.5-5H4.5L3 9Z" />
          <path d="M4 9v11h16V9" />
          <path d="M9 20v-6h6v6" />
     </svg>
);

export const IconMapPin = ({ size = 20, ...p }: IconProps) => (
     <svg {...base(size)} {...p}>
          <path d="M12 22s7-6.5 7-12a7 7 0 1 0-14 0c0 5.5 7 12 7 12Z" />
          <circle cx="12" cy="10" r="2.5" />
     </svg>
);

export const IconChevron = ({ size = 16, ...p }: IconProps) => (
     <svg {...base(size)} {...p}>
          <path d="m6 9 6 6 6-6" />
     </svg>
);

export const IconHeadset = ({ size = 16, ...p }: IconProps) => (
     <svg {...base(size)} {...p}>
          <path d="M3 14v-2a9 9 0 0 1 18 0v2" />
          <rect x="2.5" y="14" width="4" height="6" rx="1.5" />
          <rect x="17.5" y="14" width="4" height="6" rx="1.5" />
     </svg>
);