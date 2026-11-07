import React from "react";
import { SettingsProvider } from "../modules/settings_module/context/settings.context";
import { UserProvider } from "../modules/user_module/context/user.context";

export default function AppProviders({ children }: { children: React.ReactNode }) {
     return (
          <SettingsProvider>
               <UserProvider>{children}</UserProvider>
          </SettingsProvider>
     );
}