// src/shared/components/modal/DeleteModal.tsx
import React from "react";
import GlobalModal from "../GlobalModal"; // 👈 ایمپورت مودال عمومی

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
    title = "حذف آیتم",
    h1 = "آیا از حذف آیتم مورد نظر اطمینان دارید؟",
    p = "بعد از حذف، دیگر قابلیت بازگردانی وجود نخواهد داشت",
}) => {
    const handleApply = () => {
        onApply(Number(id));
        onClose();
    };

    return (
        // 👈 استفاده از مودال عمومی به جای کدهای بوت‌استرپ
        <GlobalModal isOpen={isOpen} onClose={onClose}>
            <div style={{ padding: '24px 20px' }} dir="rtl">

                {/* هدر مودال */}
                <div className="d-flex justify-content-between align-items-center mb-3">
                    <h5 className="fs-15 fw-700 m-0" style={{ color: '#1e293b' }}>
                        {title}
                    </h5>
                </div>

                {/* بدنه مودال */}
                <div className="mb-4 text-right">
                    <h1 className="fs-13 fw-600 mb-2" style={{ color: '#1e293b' }}>
                        {h1}
                    </h1>
                    <p className="text-muted fs-12 m-0" style={{ lineHeight: 1.6 }}>
                        {p}
                    </p>
                </div>

                {/* دکمه‌ها */}
                <div className="d-flex gap-2">
                    <button
                        className="btn d-block w-100 h__45 btn___info rounded-3"
                        onClick={handleApply}
                    >
                        بله، مطمئنم
                    </button>
                    <button
                        className="btn d-block w-100 h__45 btn___warning rounded-3"
                        onClick={onClose}
                    >
                        خیر، انصراف
                    </button>
                </div>
            </div>
        </GlobalModal>
    );
};