// front/src/shared/components/modal/order/certificate-modal.tsx

import "../../../styles/gift.css";

interface Props {
     isOpen: boolean;
     onClose: () => void;
     onUpload: () => void;
}

export default function OrderCertificateModal({ isOpen, onClose, onUpload }: Props) {
     if (!isOpen) return null;

     return (
          <div className="cert-modal-overlay">
               <div className="cert-modal-content">
                    <div className="cert-icon-box">
                         <span style={{ fontSize: 24, fontWeight: 900, color: "#14306b" }}>!</span>
                    </div>

                    <h2 className="cert-title">برای دریافت هدیه مدارک شغلی لازم است</h2>
                    <p className="cert-desc">
                         مدرک را بارگذاری کن تا پس از تایید، هدیه‌ات را سفارش بدهی
                    </p>

                    <button type="button" className="auth-btn cert-btn-primary" onClick={onUpload}>
                         بارگذاری مدارک شغلی
                    </button>

                    <button type="button" className="cert-btn-secondary" onClick={onClose}>
                         بعداً
                    </button>
               </div>
          </div>
     );
}