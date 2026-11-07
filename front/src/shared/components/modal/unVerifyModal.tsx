
import { useRef, useState } from "react";
import { InputBox } from "../../tools/form-inputs";
import { closeOffcanvas } from "../../utils/functions";
import { MyNotification } from "../../utils/notification";

interface TheProps {
    onStore: (verify: string, unVerifyReason: string) => void;
}

export const UnVerifyModal: React.FC<TheProps> = ({ onStore }) => {

    const modalRef = useRef<HTMLDivElement | null>(null);

    const [unVerifyReason, setUnVerifyReason] = useState("");

    const store = async () => {
        if (unVerifyReason == "") {
            MyNotification('خطا', 'علت رد درخواست الزامیست', 'error');
            return
        }
        onStore("1", unVerifyReason);
        closeOffcanvas("unVerifyModal");
    };

    return (
        <>
            <div className="offcanvas offcanvas-bottom custom-offcanvas h__300 smooth-offcanvas"
                ref={modalRef}
                tabIndex={-1}
                id="unVerifyModal"
                aria-labelledby="unVerifyModalLabel"
            >
                <div className="offcanvas-header">
                    <h5 className="offcanvas-title" id="unVerifyModalLabel">رد  درخواست</h5>
                    <button type="button" className="btn-close text-reset m-0 me-auto" data-bs-dismiss="offcanvas" aria-label="بستن"></button>
                </div>
                <div className="offcanvas-body pb-0">
                    <div className="row row-sm">

                        <InputBox
                            label="علت رد درخواست"
                            name="unVerifyReason"
                            type="textarea"
                            value={unVerifyReason}
                            onChange={(val) => setUnVerifyReason(val as string)}
                            rows={10}
                            required
                        />
                    </div>
                </div>
                <div className="offcanvas-footer">
                    <button className='btn d-block w__100 h__40 btn___info me-2' onClick={store}>ثبت نظر</button>
                </div>
            </div>
        </>
    )
}
