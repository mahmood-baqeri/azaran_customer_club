// src/shared/components/error-boundary.tsx

import { Component, ErrorInfo, ReactNode } from "react";

interface Props {
     children: ReactNode;
     fallback?: ReactNode;
}

interface State {
     hasError: boolean;
     error: Error | null;
}

/**
 * Error Boundary سراسری — جلوی صفحه سفید در صورت خطای رندر یا
 * شکست در بارگذاری chunk های lazy را می‌گیرد.
 */
export default class ErrorBoundary extends Component<Props, State> {
     state: State = { hasError: false, error: null };

     static getDerivedStateFromError(error: Error): State {
          return { hasError: true, error };
     }

     componentDidCatch(error: Error, info: ErrorInfo): void {
          // در آینده می‌توان به سرویس لاگ (Sentry) وصل کرد
          console.error("[ErrorBoundary]", error, info.componentStack);
     }

     private handleReset = (): void => {
          this.setState({ hasError: false, error: null });
     };

     render(): ReactNode {
          if (!this.state.hasError) return this.props.children;
          if (this.props.fallback) return this.props.fallback;

          return (
               <div
                    dir="rtl"
                    style={{
                         display: "flex",
                         flexDirection: "column",
                         alignItems: "center",
                         justifyContent: "center",
                         minHeight: "60vh",
                         gap: 12,
                         padding: 24,
                         textAlign: "center",
                    }}
               >
                    <h2 style={{ margin: 0 }}>خطایی رخ داد</h2>
                    <p style={{ margin: 0, color: "#6b7280" }}>
                         متأسفانه در بارگذاری این بخش مشکلی پیش آمد.
                    </p>
                    <button
                         type="button"
                         onClick={this.handleReset}
                         style={{
                              padding: "8px 20px",
                              borderRadius: 8,
                              background: "#2563eb",
                              color: "#fff",
                              border: "none",
                              cursor: "pointer",
                         }}
                    >
                         تلاش مجدد
                    </button>
               </div>
          );
     }
}