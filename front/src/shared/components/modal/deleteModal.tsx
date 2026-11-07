// src/shared/components/modal/DeleteModal.tsx
import React, { useEffect, useState } from "react";
import { createPortal } from "react-dom";

interface TheProps {
    isOpen: boolean;
    onClose: () => void;
    onApply: (id: number) => void;
    id: string | number;
    title?: string;
    h1?: string;
    p?: string;
}

export const DeleteModal: React.FC<TheProps> = ({
    isOpen,
    onClose,
    onApply,
    id,
    title = "حذف پروژه",
    h1 = "آیا از حذف آیتم مورد نظر اطمینان دارید؟",
    p = "بعد از حذف، دیگر قابلیت بازگردانی وجود نخواهد داشت",
}) => {
    // برای انیمیشن ورود/خروج، کمی دیرتر unmount می‌کنیم
    const [render, setRender] = useState(isOpen);
    const [show, setShow] = useState(isOpen);

    useEffect(() => {
        if (isOpen) {
            setRender(true);
            // یک فریم صبر می‌کنیم تا transition اجرا شود
            const raf = requestAnimationFrame(() => setShow(true));
            return () => cancelAnimationFrame(raf);
        } else {
            setShow(false);
            const t = setTimeout(() => setRender(false), 300);
            return () => clearTimeout(t);
        }
    }, [isOpen]);

    // قفل اسکرول body هنگام باز بودن
    useEffect(() => {
        if (!render) return;
        const prev = document.body.style.overflow;
        document.body.style.overflow = "hidden";
        return () => {
            document.body.style.overflow = prev;
        };
    }, [render]);

    // بستن با ESC
    useEffect(() => {
        if (!isOpen) return;
        const onKey = (e: KeyboardEvent) => {
            if (e.key === "Escape") onClose();
        };
        window.addEventListener("keydown", onKey);
        return () => window.removeEventListener("keydown", onKey);
    }, [isOpen, onClose]);

    if (!render) return null;

    const handleApply = () => {
        onApply(Number(id));
        onClose();
    };

    return createPortal(
        <>
            <div
                className={`offcanvas-backdrop fade ${show ? "show" : ""}`}
                onClick={onClose}
            />
            <div
                className={`offcanvas offcanvas-bottom custom-offcanvas deleteModal h__300 smooth-offcanvas ${show ? "show" : ""}`}
                tabIndex={-1}
                id={`deleteModal-${id}`}
                aria-labelledby={`deleteModal-${id}Label`}
                role="dialog"
                aria-modal="true"
                style={{ visibility: "visible" }}
            >
                <div className="offcanvas-header">
                    <h5 className="offcanvas-title" id={`deleteModal-${id}Label`}>
                        {title}
                    </h5>
                    <button
                        type="button"
                        className="btn-close text-reset m-0 me-auto"
                        onClick={onClose}
                        aria-label="بستن"
                    />
                </div>
                <div className="offcanvas-body">
                    <div className="row row-sm">
                        <h1 className="fs-16 fw-bold mb-2">{h1}</h1>
                        <p className="text-muted fs-13">{p}</p>
                    </div>
                </div>
                <div className="offcanvas-footer d-flex gap-2">
                    <button
                        className="btn d-block w__100 h__40 btn___info"
                        onClick={handleApply}
                    >
                        بله
                    </button>
                    <button
                        className="btn d-block w__100 h__40 btn___warning"
                        onClick={onClose}
                    >
                        خیر
                    </button>
                </div>
            </div>
        </>,
        document.body
    );
};