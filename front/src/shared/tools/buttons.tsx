import React from "react";
import { Loader } from "./loader";

type Props = {
  text: string;
  onClick: () => void;
  loading?: boolean;
  className?: string;
};


const Button: React.FC<Props> = ({ text, onClick, loading = false, className = "" }) => {
  return (
    <button
      className={`btn ${className}`}
      onClick={onClick}
      disabled={loading}
    >
      {loading ? "منتظر بمانید" : text}
      {loading && <Loader />}
    </button>
  );
};

export default Button;
