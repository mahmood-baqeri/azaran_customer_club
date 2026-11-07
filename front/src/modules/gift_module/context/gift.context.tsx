/* eslint-disable react-refresh/only-export-components */
// src/modules/gift_module/context/gift.context.tsx

import React, { createContext, useState } from "react";
import type { GiftOrder } from "../interface/gift.types";

interface GiftContextType {
     lastOrder: GiftOrder | null;
     setLastOrder: (order: GiftOrder | null) => void;
}

export const GiftContext = createContext<GiftContextType>({
     lastOrder: null,
     setLastOrder: () => { },
});

export const GiftProvider = ({ children }: { children: React.ReactNode }) => {
     const [lastOrder, setLastOrder] = useState<GiftOrder | null>(null);

     return (
          <GiftContext.Provider value={{ lastOrder, setLastOrder }}>
               {children}
          </GiftContext.Provider>
     );
};