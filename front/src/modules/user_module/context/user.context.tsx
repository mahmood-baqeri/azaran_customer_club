/* eslint-disable react-refresh/only-export-components */
// src/modules/user_module/context/user.context.tsx
import React, {
     createContext,
     useCallback,
     useEffect,
     useRef,
     useState,
} from "react";
import type { UserMe, UserNatureTypes } from "../interface/user.types";
import {
     getLocalStorage,
     setLocalStorage,
} from "../../../shared/storage/local-storage";
import {
     Token,
     UserFirstname,
     UserId,
     UserLastname,
     UserMobile,
     UserNature,
     UserScoreBalance,
} from "../../../shared/constants/storage-keys";
import { userRepository } from "../repository/user.repository";

const NATURE_LABELS: Record<UserNatureTypes, string> = {
     manager: "مدیر",
     executive: "مجری",
     seller: "فروشنده",
     user: "کاربر",
};

interface UserContextType {
     user: UserMe | null;
     loading: boolean;
     setUser: (u: UserMe | null) => void;
     refreshUser: () => Promise<void>;
}

export const UserContext = createContext<UserContextType>({
     user: null,
     loading: false,
     setUser: () => { },
     refreshUser: async () => { },
});

const reconstructFromStorage = (): UserMe | null => {
     const uuid = getLocalStorage(UserId);
     if (!uuid) return null;

     const firstname = getLocalStorage(UserFirstname) ?? "";
     const lastname = getLocalStorage(UserLastname) ?? "";
     const mobile = getLocalStorage(UserMobile) ?? "";
     const rawNature = getLocalStorage(UserNature);

     const nature: UserNatureTypes =
          rawNature === "manager" ||
               rawNature === "executive" ||
               rawNature === "seller"
               ? rawNature
               : "user";

     const scoreBalance = Number(getLocalStorage(UserScoreBalance) ?? 0);

     return {
          uuid,
          name: `${firstname} ${lastname}`.trim(),
          firstname,
          lastname,
          short_name: firstname || "کاربر",
          avatar: null,
          mobile,
          is_mobile_verified: true,
          date_joined: null,
          last_active_at: null,
          referral_code: "",
          nature,
          nature_display: NATURE_LABELS[nature],
          invited_by: null,
          profile: null,
          score: {
               current_balance: Number.isFinite(scoreBalance) ? scoreBalance : 0,
               total_earned: 0,
               total_spent: 0,
          },
          job_certificates: [], // 🆕 آرایه خالی در حالت آفلاین
          favorite_answers_count: 0,
          has_answered_all_favorites: false,
     };
};

export const UserProvider = ({ children }: { children: React.ReactNode }) => {
     const [user, setUserState] = useState<UserMe | null>(() =>
          reconstructFromStorage()
     );
     const [loading, setLoading] = useState(false);
     const inFlight = useRef(false);

     const setUser = useCallback((u: UserMe | null): void => {
          setUserState(u);

          if (!u) {
               localStorage.removeItem(UserId);
               localStorage.removeItem(UserMobile);
               localStorage.removeItem(UserFirstname);
               localStorage.removeItem(UserLastname);
               localStorage.removeItem(UserNature);
               localStorage.removeItem(UserScoreBalance);
               return;
          }

          setLocalStorage(UserId, u.uuid);
          setLocalStorage(UserMobile, u.mobile);
          setLocalStorage(UserFirstname, u.firstname);
          setLocalStorage(UserLastname, u.lastname);
          setLocalStorage(UserNature, u.nature);

          if (u.score) {
               setLocalStorage(UserScoreBalance, String(u.score.current_balance));
          }
     }, []);

     const refreshUser = useCallback(async (): Promise<void> => {
          if (inFlight.current) return;

          const token = getLocalStorage(Token);
          if (!token) {
               setUserState(null);
               return;
          }

          inFlight.current = true;
          setLoading(true);

          try {
               const me = await userRepository.loadMe();
               setUser(me);
          } catch (err) {
               console.warn("[user] load failed, using storage fallback:", err);
               const fallback = reconstructFromStorage();
               if (fallback) setUserState(fallback);
          } finally {
               inFlight.current = false;
               setLoading(false);
          }
     }, [setUser]);

     useEffect(() => {
          if (getLocalStorage(Token)) {
               refreshUser();
          }
     }, [refreshUser]);

     return (
          <UserContext.Provider value={{ user, loading, setUser, refreshUser }}>
               {children}
          </UserContext.Provider>
     );
};