import { Gift } from "../../../interface/gift";
import { closeOffcanvas } from "../../utils/functions";

interface TheProps {
    selectedCount: number; // Type hint: بهتر است عدد باشد
    gift: Gift;
    onApply: () => void; // تغییر امضا: اکنون تعداد را به عنوان آرگومان می پذیرد
}

export const GiftReceiveModal: React.FC<TheProps> = ({ onApply, gift, selectedCount }) => {
    const modalId = 'GiftTakeModal';

    const receiveGift = async () => {
        closeOffcanvas(modalId);
        onApply()
    };
    const deleteCancel = async () => {
        closeOffcanvas(modalId);
    };

    return (
        <>
            <div className="offcanvas offcanvas-bottom custom-offcanvas giftModal h__300 smooth-offcanvas" tabIndex={-1} id={modalId} aria-labelledby={`${modalId}Label`}>
                <div className="offcanvas-header">
                    <h5 className="offcanvas-title" id={`${modalId}Label`}>دریافت هدیه</h5>
                    <button type="button" className="btn-close text-reset m-0 me-auto" data-bs-dismiss="offcanvas" aria-label="بستن"></button>
                </div>
                <div className="offcanvas-body">
                    <div className="row row-sm">
                        <h1>از دریافت هدیه اطمینان دارید ؟</h1>
                        <p>در صورت دریافت هدیه ، {gift.point * selectedCount} آذر از شما کسر می گردد.</p>
                    </div>
                </div>
                <div className="offcanvas-footer">
                    {/* دکمه ها اکنون بر اساس وضعیت ورودی غیرفعال/فعال می شوند */}
                    <button
                        className='btn d-block w__60 h__40 btn___info me-2 postiveBtn'
                        onClick={receiveGift}
                    >
                        بله
                    </button>
                    <button
                        className='btn d-block w__60 h__40 btn___warning negativeBtn'
                        onClick={deleteCancel}
                    >
                        خیر
                    </button>
                </div>
            </div >
        </>
    )
}
