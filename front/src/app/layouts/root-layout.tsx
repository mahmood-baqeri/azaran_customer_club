import { Suspense, useLayoutEffect } from "react";
import { Outlet, useNavigate, useNavigation } from "react-router-dom";
import { setNavigator } from "../../shared/auth/navigation";
import Preloader from "../../shared/tools/loader";

export default function RootLayout() {
     const navigation = useNavigation();
     const navigate = useNavigate();

     useLayoutEffect(() => {
          setNavigator((to: string) => navigate(to));
     }, [navigate]);

     const isLoading = navigation.state === "loading";

     return (
          <>
               {isLoading && <Preloader />}
               <Suspense fallback={<Preloader />}>
                    <Outlet />
               </Suspense>
          </>
     );
}