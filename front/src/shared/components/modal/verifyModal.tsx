
import { useRef } from "react";
import { closeOffcanvas } from "../../utils/functions";

interface TheProps {
    onStore: (verify: string, unVerifyReason: string) => void;
}

export const VerifyModal: React.FC<TheProps> = ({ onStore }) => {

    const modalRef = useRef<HTMLDivElement | null>(null);

    const store = async () => {
        onStore("2", "");
        closeOffcanvas("verifyModal");
    };


    return (
        <>
            <div className="offcanvas offcanvas-bottom custom-offcanvas h__200 smooth-offcanvas"
                ref={modalRef}
                tabIndex={-1}
                id="verifyModal"
                aria-labelledby="verifyModalLabel"
            >
                <div className="offcanvas-header">
                    <h5 className="offcanvas-title" id="verifyModalLabel">تایید  درخواست</h5>
                    <button type="button" className="btn-close text-reset m-0 me-auto" data-bs-dismiss="offcanvas" aria-label="بستن"></button>
                </div>
                <div className="offcanvas-body pb-0">
                    <div className="row row-sm">
                        <p>آیا از تایید آیتم مورد نظر اطمینان دارید ؟</p>
                    </div>
                </div>
                <div className="offcanvas-footer">

                    <button className='btn d-block w__100 h__40 btn___info me-2' onClick={store}>بله</button>
                    <button className='btn d-block w__100 h__40 btn___warning' data-bs-dismiss="offcanvas">خیر</button>

                </div>
            </div>
        </>
    )
}
