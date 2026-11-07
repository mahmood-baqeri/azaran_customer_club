import React, { ImgHTMLAttributes } from "react";

interface MyImageProps extends ImgHTMLAttributes<HTMLImageElement> {
     src?: string;
     def?: string;
}

const FALLBACK = "/assets/none.png";

export default function MyImage({
     src,
     def = FALLBACK,
     alt = "",
     ...props
}: MyImageProps) {
     // با تغییر src، خطا را ریست می‌کنیم
     const [error, setError] = React.useState(false);
     React.useEffect(() => { setError(false); }, [src]);

     const finalSrc = !src || error ? def : src;

     return (
          <img
               src={finalSrc}
               alt={alt}
               onError={() => setError(true)}
               {...props}
          />
     );
}