// front/src/modules/user_module/components/FavoriteSlider.tsx


import type { FavoriteAnswerValue } from "../interface/user.types";

// ==========================================
// کامپوننت اسلایدر (بدون تغییر نسبت به نسخه تایید شده)
// ==========================================
interface FavoriteSliderProps {
     options: { value: FavoriteAnswerValue; label: string }[];
     value?: FavoriteAnswerValue | null;
     onChange: (val: FavoriteAnswerValue) => void;
}

export const FavoriteSlider = ({ options, value, onChange }: FavoriteSliderProps) => {
     const PRIMARY_COLOR = "#0d3b66";
     const GRAY_COLOR = "#e2e8f0";

     const selectedIndex = options.findIndex((opt) => opt.value === value);

     const getActiveWidth = () => {
          if (selectedIndex === -1) return "0%";
          if (selectedIndex === options.length - 1) return "100%";
          return `${(selectedIndex / (options.length - 1)) * 100}%`;
     };

     return (
          <div className="position-relative w-100 mt-4 mb-3" dir="rtl">
               <div
                    className="position-absolute d-flex"
                    style={{ top: "12px", right: "10%", left: "10%", height: "4px", zIndex: 0 }}
               >
                    <div className="w-100 h-100 rounded-pill position-absolute" style={{ backgroundColor: GRAY_COLOR }} />
                    {selectedIndex !== -1 && (
                         <div
                              className="h-100 rounded-pill position-absolute"
                              style={{
                                   right: 0,
                                   width: getActiveWidth(),
                                   backgroundColor: PRIMARY_COLOR,
                                   transition: "width 0.3s ease-in-out",
                              }}
                         />
                    )}
               </div>

               <div className="d-flex justify-content-between align-items-start position-relative" style={{ zIndex: 1 }}>
                    {options.map((opt) => {
                         const isActive = value === opt.value;
                         return (
                              <div
                                   key={opt.value}
                                   onClick={() => onChange(opt.value)}
                                   className="d-flex flex-column align-items-center"
                                   style={{ cursor: "pointer", flex: 1 }}
                              >
                                   <div className="d-flex align-items-center justify-content-center" style={{ height: "24px", width: "100%" }}>
                                        {isActive ? (
                                             <div
                                                  style={{
                                                       width: "24px",
                                                       height: "24px",
                                                       borderRadius: "50%",
                                                       border: `5px solid ${PRIMARY_COLOR}`,
                                                       backgroundColor: "#ffffff",
                                                       zIndex: 2,
                                                       boxShadow: "0 0 0 4px #ffffff",
                                                  }}
                                             />
                                        ) : (
                                             <div
                                                  style={{
                                                       width: "12px",
                                                       height: "12px",
                                                       borderRadius: "50%",
                                                       backgroundColor: PRIMARY_COLOR,
                                                       zIndex: 2,
                                                       boxShadow: "0 0 0 4px #ffffff",
                                                  }}
                                             />
                                        )}
                                   </div>

                                   <span
                                        className="text-nowrap text-center mt-2"
                                        style={{
                                             fontSize: "12px",
                                             color: isActive ? PRIMARY_COLOR : "#6c757d",
                                             fontWeight: isActive ? "bold" : "500",
                                             transition: "color 0.2s",
                                        }}
                                   >
                                        {opt.label}
                                   </span>
                              </div>
                         );
                    })}
               </div>
          </div>
     );
};
