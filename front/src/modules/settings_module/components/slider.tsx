// src/modules/settings_module/components/slider.tsx

import { useEffect, useRef, useState } from "react";
import { DOMAIN } from "../../../shared/constants/env";
import type { SliderItem } from "../interface/settings.types";
import "../../../shared/styles/slider.css";

interface Props {
     slides: SliderItem[];
     autoPlayInterval?: number;
     showArrows?: boolean;
     showDots?: boolean;
}

export default function Slider({
     slides,
     autoPlayInterval = 5000,
     showArrows = true,
     showDots = true,
}: Props) {
     const [index, setIndex] = useState(0);
     const [paused, setPaused] = useState(false);
     const trackRef = useRef<HTMLDivElement>(null);
     const touchStartX = useRef<number | null>(null);
     const touchDeltaX = useRef<number>(0);

     const total = slides.length;

     useEffect(() => {
          if (autoPlayInterval <= 0 || paused || total <= 1) return;
          const t = setInterval(() => {
               setIndex((i) => (i + 1) % total);
          }, autoPlayInterval);
          return () => clearInterval(t);
     }, [autoPlayInterval, paused, total]);

     useEffect(() => {
          setIndex(0);
     }, [total]);

     const goTo = (i: number) => {
          if (total === 0) return;
          setIndex(((i % total) + total) % total);
     };
     const goPrev = () => goTo(index - 1);
     const goNext = () => goTo(index + 1);

     const onTouchStart = (e: React.TouchEvent) => {
          touchStartX.current = e.touches[0].clientX;
          touchDeltaX.current = 0;
          setPaused(true);
     };
     const onTouchMove = (e: React.TouchEvent) => {
          if (touchStartX.current === null) return;
          touchDeltaX.current = e.touches[0].clientX - touchStartX.current;
     };
     const onTouchEnd = () => {
          if (touchStartX.current !== null && Math.abs(touchDeltaX.current) > 40) {
               if (touchDeltaX.current < 0) goNext();
               else goPrev();
          }
          touchStartX.current = null;
          touchDeltaX.current = 0;
          setPaused(false);
     };

     const buildPhotoUrl = (photo: string | null): string => {
          if (!photo) return "/assets/placeholder-slider.png";
          if (photo.startsWith("http")) return photo;
          if (!photo.startsWith("/")) {
               return `${DOMAIN}/media/${photo}`;
          }
          return `${DOMAIN}${photo}`;
     };

     if (total === 0) return null;

     return (
          <div
               className="slider-wrapper"
               onMouseEnter={() => setPaused(true)}
               onMouseLeave={() => setPaused(false)}
               onTouchStart={onTouchStart}
               onTouchMove={onTouchMove}
               onTouchEnd={onTouchEnd}
          >
               <div
                    className="slider-track"
                    ref={trackRef}
                    style={{ transform: `translateX(${index * 100}%)` }}
               >
                    {slides.map((s) => (
                         <div className="slider-slide" key={s.id}>
                              <img
                                   src={buildPhotoUrl(s.photo)}
                                   alt={s.title || "slide"}
                                   loading="lazy"
                                   onError={(e) => {
                                        const t = e.currentTarget;
                                        if (!t.src.endsWith("/assets/placeholder-slider.png")) {
                                             t.src = "/assets/placeholder-slider.png";
                                        }
                                   }}
                              />
                              {(s.title || s.paragraph) && (
                                   <div className="slider-overlay">
                                        {s.title && <h3 className="text-white">{s.title}</h3>}
                                        {s.paragraph && <p className="text-white">{s.paragraph}</p>}
                                   </div>
                              )}
                         </div>
                    ))}
               </div>

               {showArrows && total > 1 && (
                    <>
                         <button
                              type="button"
                              className="slider-arrow slider-arrow--prev"
                              onClick={goPrev}
                              aria-label="قبلی"
                         >
                              ›
                         </button>
                         <button
                              type="button"
                              className="slider-arrow slider-arrow--next"
                              onClick={goNext}
                              aria-label="بعدی"
                         >
                              ‹
                         </button>
                    </>
               )}

               {showDots && total > 1 && (
                    <div className="slider-dots">
                         {slides.map((_, i) => (
                              <button
                                   key={i}
                                   type="button"
                                   className={`slider-dot ${i === index ? "active" : ""}`}
                                   onClick={() => goTo(i)}
                                   aria-label={`اسلاید ${i + 1}`}
                              />
                         ))}
                    </div>
               )}
          </div>
     );
}