import { useNavigate } from "react-router-dom";

export const useGoBack = () => {
  const navigate = useNavigate();
  return (fallback = "/") => {
    if (window.history.state && window.history.state.idx > 0) navigate(-1);
    else navigate(fallback);
  };
};