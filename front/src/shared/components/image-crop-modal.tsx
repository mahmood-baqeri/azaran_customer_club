// src/shared/components/image-crop-modal.tsx

import { useCallback, useState } from "react";
import Cropper, { type Area } from "react-easy-crop";
import "../styles/AuthTemplate.css";

interface Props {
     imageSrc: string;
     onCancel: () => void;
     onConfirm: (blob: Blob) => void;
     aspect?: number;
}

async function getCroppedBlob(imageSrc: string, crop: Area): Promise<Blob> {
     const image = await new Promise<HTMLImageElement>((resolve, reject) => {
          const img = new Image();
          img.crossOrigin = "anonymous";
          img.onload = () => resolve(img);
          img.onerror = reject;
          img.src = imageSrc;
     });

     const canvas = document.createElement("canvas");
     canvas.width = crop.width;
     canvas.height = crop.height;
     const ctx = canvas.getContext("2d");
     if (!ctx) throw new Error("Canvas context failed");

     ctx.drawImage(
          image,
          crop.x,
          crop.y,
          crop.width,
          crop.height,
          0,
          0,
          crop.width,
          crop.height
     );

     return new Promise((resolve, reject) => {
          canvas.toBlob(
               (blob) => (blob ? resolve(blob) : reject(new Error("toBlob failed"))),
               "image/jpeg",
               0.9
          );
     });
}

export default function ImageCropModal({
     imageSrc,
     onCancel,
     onConfirm,
     aspect = 1,
}: Props) {
     const [crop, setCrop] = useState({ x: 0, y: 0 });
     const [zoom, setZoom] = useState(1);
     const [croppedArea, setCroppedArea] = useState<Area | null>(null);
     const [processing, setProcessing] = useState(false);

     const onCropComplete = useCallback((_a: Area, areaPixels: Area) => {
          setCroppedArea(areaPixels);
     }, []);

     const handleConfirm = async () => {
          if (!croppedArea) return;
          setProcessing(true);
          try {
               const blob = await getCroppedBlob(imageSrc, croppedArea);
               onConfirm(blob);
          } catch (err) {
               console.error("[crop] failed:", err);
          } finally {
               setProcessing(false);
          }
     };

     return (
          <div
               style={{
                    position: "fixed",
                    inset: 0,
                    background: "rgba(0,0,0,0.9)",
                    zIndex: 9999,
                    display: "flex",
                    flexDirection: "column",
               }}
          >
               <div style={{ flex: 1, position: "relative" }}>
                    <Cropper
                         image={imageSrc}
                         crop={crop}
                         zoom={zoom}
                         aspect={aspect}
                         cropShape="round"
                         showGrid={false}
                         onCropChange={setCrop}
                         onZoomChange={setZoom}
                         onCropComplete={onCropComplete}
                    />
               </div>

               <div
                    style={{
                         padding: 16,
                         background: "#fff",
                         display: "flex",
                         flexDirection: "column",
                         gap: 12,
                         direction: "rtl",
                    }}
               >
                    <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                         <span style={{ fontSize: 12, color: "#14306b" }}>زوم</span>
                         <input
                              type="range"
                              min={1}
                              max={3}
                              step={0.05}
                              value={zoom}
                              onChange={(e) => setZoom(Number(e.target.value))}
                              style={{ flex: 1 }}
                         />
                    </div>
                    <div style={{ display: "flex", gap: 10 }}>
                         <button
                              className="auth-btn"
                              style={{ flex: 1 }}
                              onClick={handleConfirm}
                              disabled={processing}
                         >
                              {processing ? "در حال پردازش..." : "تایید و آپلود"}
                         </button>
                         <button
                              className="auth-btn"
                              style={{ flex: 1, background: "#c5cee0" }}
                              onClick={onCancel}
                              disabled={processing}
                         >
                              انصراف
                         </button>
                    </div>
               </div>
          </div>
     );
}