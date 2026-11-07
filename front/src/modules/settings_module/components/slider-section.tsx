// src/modules/settings_module/components/slider-section.tsx

import { useSliders } from "../hooks/use-sliders";
import Slider from "./slider";
import "../../../shared/styles/slider.css";

export default function SliderSection() {
     const { sliders, loading, error } = useSliders();

     if (loading && sliders.length === 0) {
          return <div className="slider-skeleton" />;
     }
     if (error && sliders.length === 0) return null;
     if (sliders.length === 0) return null;

     return <Slider slides={sliders} autoPlayInterval={9000} showArrows={false} />;
}