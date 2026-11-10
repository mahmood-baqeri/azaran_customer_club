// src/shared/components/Pagination.tsx


import "../../shared/styles/pagination.css";

interface PaginationProps {
     /** صفحه فعلی (از ۱ شروع می‌شود) */
     currentPage: number;
     /** تعداد کل صفحات */
     totalPages: number;
     /** تابعی که هنگام کلیک روی دکمه‌ها صدا زده می‌شود */
     onPageChange: (page: number) => void;
     /** غیرفعال کردن کل کامپوننت هنگام لود شدن */
     disabled?: boolean;
}

export default function Pagination({
     currentPage,
     totalPages,
     onPageChange,
     disabled = false,
}: PaginationProps) {

     // منطق تولید شماره صفحات به سبک گوگل
     const getPaginationItems = (): (number | string)[] => {
          const items: (number | string)[] = [];

          if (totalPages <= 6) {
               // اگر تعداد صفحات کم بود، همه را نشان بده
               for (let i = 1; i <= totalPages; i++) items.push(i);
               return items;
          }

          // صفحه اول همیشه نمایش داده می‌شود
          items.push(1);

          if (currentPage > 3) {
               items.push("...");
          }

          // محاسبه بازه حول صفحه فعلی
          const start = Math.max(2, currentPage - 1);
          const end = Math.min(totalPages - 1, currentPage + 1);

          for (let i = start; i <= end; i++) {
               items.push(i);
          }

          if (currentPage < totalPages - 2) {
               items.push("...");
          }

          // صفحه آخر همیشه نمایش داده می‌شود
          items.push(totalPages);

          return items;
     };

     const pages = getPaginationItems();

     return (
          <div className="custom-pagination">
               <button
                    className="cp-btn cp-nav"
                    disabled={currentPage === 1 || disabled}
                    onClick={() => onPageChange(currentPage - 1)}
                    aria-label="قبلی"
               >
                    <i className="icon-arrow-right-3"></i>
               </button>

               {pages.map((p, index) => {
                    if (p === "...") {
                         return (
                              <span key={`ellipsis-${index}`} className="cp-dots">
                                   ...
                              </span>
                         );
                    }

                    const pageNumber = p as number;
                    const isActive = pageNumber === currentPage;

                    return (
                         <button
                              key={pageNumber}
                              className={`cp-btn ${isActive ? "active" : ""}`}
                              disabled={disabled}
                              onClick={() => onPageChange(pageNumber)}
                         >
                              {pageNumber.toLocaleString("fa-IR")}
                         </button>
                    );
               })}

               <button
                    className="cp-btn cp-nav"
                    disabled={currentPage === totalPages || disabled}
                    onClick={() => onPageChange(currentPage + 1)}
                    aria-label="بعدی"
               >
                    <i className="icon-arrow-left-2"></i>
               </button>
          </div>
     );
}