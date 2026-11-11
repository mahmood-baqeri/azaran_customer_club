import { FaChevronLeft } from 'react-icons/fa';
import "../../../shared/styles/supportModal.css";
import MyImage from '../../../shared/components/image-show';
import { ICONS } from '../../../shared/constants/icons';
import GlobalModal from '../../../shared/components/GlobalModal';
import { SUPPORT_ROUTES } from '../../support_module/routes';
import { Link } from 'react-router-dom';

interface Props {
     isOpen: boolean;
     onClose: () => void;
     onCall?: () => void;
     onMessage?: () => void;
}

export default function SupportModal({ isOpen, onClose }: Props) {
     return (
          < GlobalModal isOpen={isOpen} onClose={onClose} >
               < div style={{ padding: '20px' }}>

                    < div className="support-modal-header" >
                         <h2 className="support-modal-title">پشتیبانی</h2>
                         <p className="support-modal-subtitle">چطور می‌خواهید با ما در ارتباط باشید؟</p>
                    </div >

                    < div className="support-modal-body" >
                         {/* دکمه تماس */}
                         <a href="tel:09103143105" className="support-action-card" onClick={onClose} >
                              <div className="support-action-content">
                                   <div className="support-icon-box">
                                        <MyImage src={ICONS.phone} className="support-icon-img" />
                                   </div>
                                   <div className="support-action-texts">
                                        <span className="support-action-title">تماس با پشتیبانی</span>
                                        <span className="support-action-subtitle fs-11 fw-400">صحبت مستقیم با کارشناس باشگاه</span>
                                   </div>
                              </div>
                              <FaChevronLeft className="support-action-chevron" size={14} />
                         </a>

                         {/* دکمه پیام */}
                         <Link to={SUPPORT_ROUTES.create} className="support-action-card">
                              <div className="support-action-content">
                                   <div className="support-icon-box">
                                        <MyImage src={ICONS.message} className="support-icon-img" />
                                   </div>
                                   <div className="support-action-texts">
                                        <span className="support-action-title">پیام به پشتیبانی</span>
                                        <span className="support-action-subtitle fs-11 fw-400">سؤال، انتقاد یا پیشنهاد بنویسید و پاسخ بگیرید</span>
                                   </div>
                              </div>
                              <FaChevronLeft className="support-action-chevron" size={14} />
                         </Link >

                         {/* دکمه انصراف */}
                         < button className="support-cancel-btn" onClick={onClose} >  انصراف </button >
                    </div >
               </div >
          </GlobalModal >
     );
}