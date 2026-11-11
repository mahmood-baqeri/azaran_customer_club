// src/shared/components/route-loader.tsx

import { useEffect, useRef, useState } from "react";
import { useLocation, type Location } from "react-router-dom";
import { MainPreloader } from "../tools/loader";

const MIN_VISIBLE_MS = 350;
const EXIT_MS = 180;

type Phase = "idle" | "showing" | "exiting";

interface TrackedState {
     location: Location;
     phase: Phase;
}

export default function RouteLoader() {
     const location = useLocation();

     const [tracked, setTracked] = useState<TrackedState>({
          location,
          phase: "idle",
     });

     const timerRef = useRef<number | null>(null);

     // ✅ الگوی رسمی React: تنظیم state حین رندر
     // این setState قبل از commit اجرا می‌شود، بنابراین لودر
     // در همان فریم اول همراه با صفحه‌ی جدید ظاهر می‌شود.
     if (tracked.location !== location) {
          setTracked({ location, phase: "showing" });
     }

     useEffect(() => {
          // پاک‌سازی تایمر قبلی
          if (timerRef.current !== null) {
               window.clearTimeout(timerRef.current);
               timerRef.current = null;
          }

          if (tracked.phase === "showing") {
               timerRef.current = window.setTimeout(() => {
                    setTracked((prev) =>
                         prev.phase === "showing"
                              ? { ...prev, phase: "exiting" }
                              : prev
                    );
               }, MIN_VISIBLE_MS);
          } else if (tracked.phase === "exiting") {
               timerRef.current = window.setTimeout(() => {
                    setTracked((prev) =>
                         prev.phase === "exiting"
                              ? { ...prev, phase: "idle" }
                              : prev
                    );
               }, EXIT_MS);
          }

          return () => {
               if (timerRef.current !== null) {
                    window.clearTimeout(timerRef.current);
                    timerRef.current = null;
               }
          };
     }, [tracked]);

     if (tracked.phase === "idle") return null;
     return <MainPreloader exiting={tracked.phase === "exiting"} />;
}