import { Link } from "react-router-dom";
import "../../shared/styles/footer.css"

const ROUTES = {
     score: "/score",
     gifts: "/gifts",
     home_page: "/",
};

export default function Footer() {
     return (
          <div className="footer-nav-area" id="footerNav">
               <div className="suha-footer-nav">
                    <ul className="h-100 d-flex align-items-center justify-content-between ps-0 rtl-flex-d-row-r">
                         <li>
                              <Link to={ROUTES.score}>
                                   <i className="icon-star-1"></i>گردش حساب
                              </Link>
                         </li>
                         <li>
                              <Link to={ROUTES.gifts}>
                                   <i className="icon-gift"></i>هدایا
                              </Link>
                         </li>
                         <li className="center">
                              <Link to={ROUTES.home_page}>
                                   <i className="icon-home"></i>
                              </Link>
                         </li>
                         <li className="disabled_2">
                              <Link to="">
                                   <i className="icon-radio"></i>اخبار
                              </Link>
                         </li>
                         <li>
                              <Link to="">
                                   <i className="icon-ram"></i>مالی و اداری
                              </Link>
                         </li>
                    </ul>
               </div>
          </div>
     );
}