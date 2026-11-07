// front/src/app/router.tsx

import { lazy, Suspense, useLayoutEffect } from "react";
import { Routes, Route, useNavigate, useLocation } from "react-router-dom";
import { setNavigator } from "../shared/auth/navigation";
import MainLayout from "./layouts/main-layout";
import { AUTH_ROUTES } from "../modules/auth_module/routes";
import Preloader from "../shared/tools/loader";
import GuestGuard from "../modules/auth_module/components/guest-guard";
import AuthGuard from "../modules/auth_module/components/auth-guard";
import { PROFILE_ROUTES } from "../modules/user_module/routes";
import { NOTIFICATIONS_ROUTES } from "../modules/notifications_module/routes";
import { GIFT_ROUTES } from "../modules/gift_module/routes";
import { PROMOTION_ROUTES } from "../modules/promotion_module/routes";
import { FAQ_ROUTES } from "../modules/faq_module/routes";
import { PROJECT_ROUTES } from "../modules/project_module/routes";

const LoginScreen = lazy(() => import("../modules/auth_module/screens/login.screen"));
const OtpScreen = lazy(() => import("../modules/auth_module/screens/otp.screen"));
const PasswordLoginScreen = lazy(() => import("../modules/auth_module/screens/password-login.screen"));
const WelcomeScreen = lazy(() => import("../modules/auth_module/screens/welcome.screen"));
const RegisterScreen = lazy(() => import("../modules/auth_module/screens/register.screen"));
const HomePage = lazy(() => import("../modules/home_module/screens/home.screen"));
const NotificationScreen = lazy(() => import("../modules/notifications_module/screens/notification.screen"));

const ProfileScreen = lazy(() => import("../modules/user_module/screen/profile.screen"));
const CompletionScreen = lazy(() => import("../modules/user_module/screen/completion.screen"));
const FavoriteScreen = lazy(() => import("../modules/user_module/screen/favorite.screen"));

const GiftsScreen = lazy(() => import("../modules/gift_module/screen/gifts.screen"));
const GiftDetailScreen = lazy(() => import("../modules/gift_module/screen/gift_detail.screen"));
const OrdersScreen = lazy(() => import("../modules/gift_module/screen/orders.screen"));
const OrderDetailScreen = lazy(() => import("../modules/gift_module/screen/order_detail.screen"));

const PromotionsScreen = lazy(() => import("../modules/promotion_module/screen/promotions.screen"));
const PromotionOrdersScreen = lazy(() => import("../modules/promotion_module/screen/promotion_orders.screen"));
const PromotionOrderDetailScreen = lazy(() => import("../modules/promotion_module/screen/promotion_order_detail.screen"));

const SuccessfulOrderScreen = lazy(() => import("../modules/page_module/screen/successful_order.screen"));

const FaqListScreen = lazy(() => import("../modules/faq_module/screen/faq-list.screen"));
const FaqDetailScreen = lazy(() => import("../modules/faq_module/screen/faq-detail.screen"));

const CreateProjectScreen = lazy(() => import("../modules/project_module/screen/create_project.screen"));
const EditProjectScreen = lazy(() => import("../modules/project_module/screen/edit_project.screen"));
const UploadAttachmentsScreen = lazy(() => import("../modules/project_module/screen/upload_attachments.screen"));
const ProjectsListScreen = lazy(() => import("../modules/project_module/screen/projects_list.screen"));
const ProjectDetailScreen = lazy(() => import("../modules/project_module/screen/project_detail.screen"));
const ColleaguesScreen = lazy(() => import("../modules/project_module/screen/colleagues.screen"));


export default function AppRouter() {
     const navigate = useNavigate();
     const location = useLocation();

     useLayoutEffect(() => {
          setNavigator((to: string) => navigate(to));
     }, [navigate]);

     return (
          <Suspense fallback={<Preloader />}>
               <Routes>
                    <Route element={<GuestGuard />}>
                         <Route path={AUTH_ROUTES.login} element={<LoginScreen />} />
                         <Route path={AUTH_ROUTES.otp} element={<OtpScreen />} />
                         <Route path={AUTH_ROUTES.password} element={<PasswordLoginScreen />} />
                    </Route>

                    <Route element={<AuthGuard />}>

                         <Route path={AUTH_ROUTES.register} element={<RegisterScreen />} />
                         <Route path={AUTH_ROUTES.welcome} element={<WelcomeScreen />} />

                         <Route element={<MainLayout />}>
                              <Route path="/" element={<HomePage key={location.key} />} />

                              <Route path={NOTIFICATIONS_ROUTES.all} element={<NotificationScreen />} />

                              <Route path={PROFILE_ROUTES.completion} element={<CompletionScreen />} />
                              <Route path={PROFILE_ROUTES.profile} element={<ProfileScreen />} />
                              <Route path={PROFILE_ROUTES.favorite} element={<FavoriteScreen />} />

                              {/* Gift Routes */}
                              <Route path={GIFT_ROUTES.list} element={<GiftsScreen />} />
                              <Route path={GIFT_ROUTES.detail(":id")} element={<GiftDetailScreen />} />
                              <Route path={GIFT_ROUTES.orders} element={<OrdersScreen />} />
                              <Route path={GIFT_ROUTES.orderDetail(":id")} element={<OrderDetailScreen />} />
                              <Route path={GIFT_ROUTES.success(":id")} element={<SuccessfulOrderScreen type="gift" />} />

                              {/* Promotion Routes */}
                              <Route path={PROMOTION_ROUTES.list} element={<PromotionsScreen />} />
                              <Route path={PROMOTION_ROUTES.orders} element={<PromotionOrdersScreen />} />
                              <Route path={PROMOTION_ROUTES.success(":id")} element={<SuccessfulOrderScreen type="promotion" />} />
                              <Route path={PROMOTION_ROUTES.orderDetail(":id")} element={<PromotionOrderDetailScreen />} />

                              <Route path={FAQ_ROUTES.list} element={<FaqListScreen />} />
                              <Route path={FAQ_ROUTES.detail(":id")} element={<FaqDetailScreen />} />


                              <Route path={PROJECT_ROUTES.list} element={<ProjectsListScreen />} />
                              <Route path={PROJECT_ROUTES.create} element={<CreateProjectScreen />} />
                              <Route path={PROJECT_ROUTES.upload(":id")} element={<UploadAttachmentsScreen />} />
                              <Route path={PROJECT_ROUTES.edit(":id")} element={<EditProjectScreen />} />
                              <Route path={PROJECT_ROUTES.detail(":id")} element={<ProjectDetailScreen />} />
                              <Route path={PROJECT_ROUTES.colleagues(":id")} element={<ColleaguesScreen />} />

                         </Route>
                    </Route>
               </Routes>
          </Suspense>
     );
}