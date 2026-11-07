// src/modules/faq_module/components/BottomInputBar.tsx
import { useState } from "react";

interface Props {
     placeholder: string;
     onSubmit: (text: string) => Promise<boolean>;
     submitting: boolean;
}

export default function BottomInputBar({ placeholder, onSubmit, submitting }: Props) {
     const [text, setText] = useState("");
     const isDisabled = !text.trim() || submitting;

     const handleSubmit = async () => {
          if (isDisabled) return;
          const success = await onSubmit(text.trim());
          if (success) setText("");
     };

     return (
          <div className="faq-bottom-bar">
               <button
                    className={`faq-send-btn ${isDisabled ? "disabled" : ""}`}
                    onClick={handleSubmit}
                    disabled={isDisabled}
               >
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="22" y1="2" x2="11" y2="13" /><polygon points="22 2 15 22 11 13 2 9 22 2" /></svg>
               </button>
               <textarea
                    className="faq-input"
                    placeholder={placeholder}
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
               />
          </div>
     );
}