// src/modules/auth_module/screens/login.screen.tsx


import MyImage from "../../../shared/components/image-show";
import { APPLEVEL } from "../../../shared/constants/env";
import { ICONS } from "../../../shared/constants/icons";
import "../../../shared/styles/AuthTemplate.css";


export default function AuthFootbar() {
     return (
          <div className="auth-footbar">
               <span className="foot-support">
                    <MyImage src={ICONS.support} height={14} width={14} className="img" alt="photo" />
                    <span className="mt-1"> پشتیبانی</span>
               </span>

               <span>نسخه {APPLEVEL}</span>

               <span></span>
               <span></span>
          </div>
     );
}