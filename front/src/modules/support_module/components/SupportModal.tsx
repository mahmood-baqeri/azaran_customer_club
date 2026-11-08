import { FaChevronLeft } from 'react-icons/fa';
import "../../../shared/styles/supportModal.css";
import MyImage from '../../../shared/components/image-show';
import { ICONS } from '../../../shared/constants/icons';
import GlobalModal from '../../../shared/components/GlobalModal';

interface Props {
     isOpen: boolean;
     onClose: () => void;
     onCall?: () => void;
     onMessage?: () => void;
}

export default function SupportModal({ isOpen, onClose, onCall, onMessage }: Props) {
     return (
          < GlobalModal isOpen={isOpen} onClose={onClose} >
               < div style={{ padding: '20px' }}>

                    < div className="support-modal-header" >
                         <h2 className="support-modal-title">پشتیبانی</h2>
                         <p className="support-modal-subtitle">چطور می‌خواهید با ما در ارتباط باشید؟</p>
                    </div >

                    < div className="support-modal-body" >
                         {/* دکمه تماس */}
                         < div className="support-action-card" onClick={() => { if (onCall) onCall(); else onClose(); }}>
                              <div className="support-action-content">
                                   <div className="support-icon-box">
                                        <MyImage src={ICONS.phone} className="support-icon-img" />
                                   </div>
                                   <div className="support-action-texts">
                                        <span className="support-action-title">تماس با پشتیبانی</span>
                                        <span className="support-action-subtitle">صحبت مستقیم با کارشناس باشگاه</span>
                                   </div>
                              </div>
                              <FaChevronLeft className="support-action-chevron" size={14} />
                         </div >

                         {/* دکمه پیام */}
                         < div className="support-action-card" onClick={() => { if (onMessage) onMessage(); else onClose(); }}>
                              <div className="support-action-content">
                                   <div className="support-icon-box">
                                        <MyImage src={ICONS.message} className="support-icon-img" />
                                   </div>
                                   <div className="support-action-texts">
                                        <span className="support-action-title">پیام به پشتیبانی</span>
                                        <span className="support-action-subtitle">سؤال، انتقاد یا پیشنهاد بنویسید و پاسخ بگیرید</span>
                                   </div>
                              </div>
                              <FaChevronLeft className="support-action-chevron" size={14} />
                         </div >

                         {/* دکمه انصراف */}
                         < button className="support-cancel-btn" onClick={onClose} >  انصراف </button >
                    </div >
               </div >
          </GlobalModal >
     );
}