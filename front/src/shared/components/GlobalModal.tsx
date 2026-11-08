import { useState, useEffect, ReactNode } from 'react';
import "../styles/global-modal.css";

interface Props {
     isOpen: boolean;
     onClose: () => void;
     children: ReactNode;
}

export default function GlobalModal({ isOpen, onClose, children }: Props) {
     const [isMounted, setIsMounted] = useState(false);
     const [isVisible, setIsVisible] = useState(false);

     useEffect(() => {
          if (isOpen) {
               setIsMounted(true);
               // تاخیر خیلی کوتاه برای اینکه مرورگر فرصت رندر اولیه را داشته باشد
               const timer = setTimeout(() => setIsVisible(true), 10);
               return () => clearTimeout(timer);
          } else {
               setIsVisible(false);
               // زمان بسته شدن انیمیشن (باید با زمان transition در CSS یکی باشد)
               const timer = setTimeout(() => setIsMounted(false), 300);
               return () => clearTimeout(timer);
          }
     }, [isOpen]);

     if (!isMounted) return null;

     return (
          <div
               className={`global-modal-overlay ${isVisible ? 'is-visible' : ''}`}
               onClick={onClose}
          >
               <div
                    className={`global-modal-sheet ${isVisible ? 'is-visible' : ''}`}
                    onClick={(e) => e.stopPropagation()}
               >
                    {children}
               </div>
          </div>
     );
}