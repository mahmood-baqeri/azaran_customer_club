// src/modules/learn_module/screen/learn_detail.screen.tsx

import { useParams } from "react-router-dom";
import Header from "../../../app/layouts/header";
import { useLearnDetail } from "../hooks/use-learn-detail";
import "../../../shared/styles/learn.css";
import { handel_photo_address } from "../../../shared/utils/handler";

export default function LearnDetailScreen() {
  const { id } = useParams<{ id: string }>();
  const learnId = id ? Number(id) : null;
  const { learn, loading } = useLearnDetail(learnId);



  if (loading) return <div className="text-center mt-5 text-muted">در حال بارگذاری...</div>;
  if (!learn) return <div className="text-center mt-5">آموزش یافت نشد.</div>;

  return (
    <>
      <Header title={learn.title} showBack showLogo={false} menuBg="f7f8fb" buttonBg="e8eefc" />

      <div className="learn-detail-body">
        {learn.photo && (
          <div className="learn-detail-img">
            <img src={handel_photo_address(learn.photo)} alt={learn.title} />
          </div>
        )}

        <h1 className="learn-detail-title">{learn.title}</h1>

        <div className="learn-detail-meta">
          <span>زمان مطالعه: {learn.time || "کوتاه"} دقیقه</span>
        </div>

        {learn.caption && (
          <p className="learn-detail-caption">{learn.caption}</p>
        )}

        {/* متن اصلی آموزش */}
        <div
          className="learn-detail-content prose"
          dangerouslySetInnerHTML={{ __html: learn.full_text || "" }}
        />
      </div>
    </>
  );
}