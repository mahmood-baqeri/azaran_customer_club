// src/modules/user_module/hooks/use-avatar-upload.ts

import { useCallback, useRef, useState } from "react";
import { userRepository } from "../repository/user.repository";
import { useUser } from "./use-user";
import { MyNotification } from "../../../shared/utils/notification";
import { getErrorMessage } from "../../../shared/api/errors";

const MAX_SIZE = 5 * 1024 * 1024;

export const useAvatarUpload = () => {
  const { setUser } = useUser();
  const [cropImage, setCropImage] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const pickFile = useCallback(() => {
    fileInputRef.current?.click();
  }, []);

  const handleFileChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (!file) return;

      if (!file.type.startsWith("image/")) {
        MyNotification("", "فقط تصویر مجاز است.", "error");
        return;
      }
      if (file.size > MAX_SIZE) {
        MyNotification("", "حجم تصویر بیشتر از ۵ مگابایت است.", "error");
        return;
      }

      const reader = new FileReader();
      reader.onload = () => setCropImage(reader.result as string);
      reader.readAsDataURL(file);

      if (fileInputRef.current) fileInputRef.current.value = "";
    },
    []
  );

  const cancelCrop = useCallback(() => setCropImage(null), []);

  const confirmCrop = useCallback(
    async (blob: Blob) => {
      setCropImage(null);
      setUploading(true);
      try {
        const file = new File([blob], "avatar.jpg", { type: "image/jpeg" });
        const updated = await userRepository.uploadAvatar(file);
        setUser(updated);
        MyNotification("", "آواتار به‌روزرسانی شد.", "success");
      } catch (err) {
        console.error("[avatar] upload failed:", err);
        MyNotification("اخطار ! ", getErrorMessage(err, "آپلود آواتار ناموفق بود."), "error");
      } finally {
        setUploading(false);
      }
    },
    [setUser]
  );

  return {
    fileInputRef,
    cropImage,
    uploading,
    pickFile,
    handleFileChange,
    cancelCrop,
    confirmCrop,
  };
};