//  front/src/modules/settings_module/context/settings.context.tsx

import React, {
     createContext,
     useCallback,
     useEffect,
     useRef,
     useState,
} from "react";
import { settingsRepository } from "../repository/settings.repository";
import type { SettingInterface } from "../interface/settings.types";
import { getLocalStorage } from "../../../shared/storage/local-storage";
import { Token } from "../../../shared/constants/storage-keys";

interface SettingsContextType {
     settings: SettingInterface | null;
     loading: boolean;
     refreshSettings: () => Promise<void>;
}

// eslint-disable-next-line react-refresh/only-export-components
export const SettingsContext = createContext<SettingsContextType>({
     settings: null,
     loading: false,
     refreshSettings: async () => { },
});

export const SettingsProvider = ({ children }: { children: React.ReactNode }) => {
     const [settings, setSettings] = useState<SettingInterface | null>(null);
     const [loading, setLoading] = useState(false);
     const inFlight = useRef(false);

     const refreshSettings = useCallback(async () => {
          if (inFlight.current) return;
          if (!getLocalStorage(Token)) {
               setSettings(null);
               return;
          }
          inFlight.current = true;
          setLoading(true);
          try {
               const s = await settingsRepository.load();
               setSettings(s);
          } catch (err) {
               console.error("[settings] load failed:", err);
          } finally {
               inFlight.current = false;
               setLoading(false);
          }
     }, []);

     // ✅ فقط یک بار در mount (اگر لاگین بود)
     useEffect(() => {
          refreshSettings();
          // eslint-disable-next-line react-hooks/exhaustive-deps
     }, []);

     return (
          <SettingsContext.Provider value={{ settings, loading, refreshSettings }}>
               {children}
          </SettingsContext.Provider>
     );
};