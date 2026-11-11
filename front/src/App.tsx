// front/src/App.tsx

import AppRouter from "./app/router";
import RouteLoader from "./shared/components/route-loader";

export default function App() {
  return (
    <>
      <AppRouter />
      <RouteLoader />
    </>
  );
}