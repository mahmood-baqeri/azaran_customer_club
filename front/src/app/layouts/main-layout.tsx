//  front/src/app/layouts/main-layout.tsx

import { Outlet } from "react-router-dom";
// import Footer from "./footer";

export default function MainLayout() {
     return (
          <>
               <div
                    className="page-content-wrapper container"
                    dir="rtl"
                    lang="fa"
               >
                    <Outlet />
               </div>
               {/* <Footer /> */}
          </>
     );
}