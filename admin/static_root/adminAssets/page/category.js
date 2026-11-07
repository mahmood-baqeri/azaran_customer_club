$(document).ready(function () {

     // =============================================
     // انتخاب همه / لغو انتخاب
     // =============================================
     $('#checkAll').change(function () {
          $('.category-checkbox').prop('checked', $(this).prop('checked'));
          updateSelectedCount();
     });

     $('#selectAll').click(function () {
          $('.category-checkbox').prop('checked', true);
          $('#checkAll').prop('checked', true);
          updateSelectedCount();
     });

     $('#deselectAll').click(function () {
          $('.category-checkbox').prop('checked', false);
          $('#checkAll').prop('checked', false);
          updateSelectedCount();
     });

     $('.category-checkbox').change(updateSelectedCount);

     function updateSelectedCount() {
          const count = $('.category-checkbox:checked').length;
          $('#selectedCount').text(count + ' انتخاب شده');
          $('#checkAll').prop(
               'checked',
               $('.category-checkbox:checked').length === $('.category-checkbox').length && $('.category-checkbox').length > 0
          );
     }

     // =============================================
     // toggle وضعیت
     // =============================================
     $('.status-badge').click(function () {
          const $badge = $(this);
          const id = $badge.data('id');

          Swal.fire({
               title: 'تغییر وضعیت',
               text: 'آیا از تغییر وضعیت این دسته‌بندی اطمینان دارید؟',
               icon: 'question',
               showCancelButton: true,
               confirmButtonText: 'بله، تغییر کن',
               cancelButtonText: 'لغو',
          }).then((result) => {
               if (!result.isConfirmed) return;

               $.ajax({
                    url: '/manager/category/toggle-status/',
                    type: 'POST',
                    data: {
                         id: id,
                         csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val()
                    },
                    success: function (response) {
                         if (response.success) {
                              const newStatus = response.is_active;
                              $badge
                                   .removeClass('bg-success bg-danger')
                                   .addClass(newStatus ? 'bg-success' : 'bg-danger')
                                   .text(newStatus ? 'فعال' : 'غیرفعال')
                                   .data('status', newStatus ? 'true' : 'false');

                              Swal.fire({
                                   icon: 'success', title: 'موفق',
                                   text: response.message,
                                   timer: 2000, showConfirmButton: false
                              });
                         }
                    },
                    error: function () {
                         Swal.fire({ icon: 'error', title: 'خطا', text: 'مشکلی در تغییر وضعیت رخ داد' });
                    }
               });
          });
     });

     // =============================================
     // حذف
     // =============================================
     $('.delete-category').click(function () {
          const id = $(this).data('id');
          const row = $(this).closest('tr');

          Swal.fire({
               title: 'حذف دسته‌بندی',
               text: 'آیا از حذف این دسته‌بندی اطمینان دارید؟',
               icon: 'warning',
               showCancelButton: true,
               confirmButtonText: 'بله، حذف کن',
               cancelButtonText: 'لغو',
               confirmButtonColor: '#dc3545',
          }).then((result) => {
               if (!result.isConfirmed) return;

               $.ajax({
                    url: '/manager/category/delete/',
                    type: 'POST',
                    data: {
                         id: id,
                         csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val()
                    },
                    success: function (response) {
                         if (response.success) {
                              row.fadeOut(500, function () {
                                   $(this).remove();
                                   updateSelectedCount();
                              });
                              Swal.fire({
                                   icon: 'success', title: 'حذف شد',
                                   text: response.message,
                                   timer: 2000, showConfirmButton: false
                              });
                         } else {
                              Swal.fire({ icon: 'error', title: 'خطا', text: response.error });
                         }
                    },
                    error: function () {
                         Swal.fire({ icon: 'error', title: 'خطا', text: 'مشکلی در حذف رخ داد' });
                    }
               });
          });
     });

     // =============================================
     // عملیات دسته‌جمعی
     // =============================================
     $('.bulk-action').click(function () {
          const action = $(this).data('action');
          const ids = $('.category-checkbox:checked').map(function () {
               return $(this).val();
          }).get();

          if (ids.length === 0) {
               Swal.fire({ icon: 'warning', title: 'هشدار', text: 'لطفاً حداقل یک دسته‌بندی را انتخاب کنید' });
               return;
          }

          const actionLabels = {
               'delete': { title: 'حذف دسته‌جمعی', text: `${ids.length} دسته‌بندی حذف خواهند شد`, confirmText: 'بله، حذف کن', icon: 'warning', color: '#dc3545' },
               'activate': { title: 'فعال‌سازی دسته‌جمعی', text: `${ids.length} دسته‌بندی فعال خواهند شد`, confirmText: 'بله، فعال کن', icon: 'success', color: '#28a745' },
               'deactivate': { title: 'غیرفعال‌سازی دسته‌جمعی', text: `${ids.length} دسته‌بندی غیرفعال خواهند شد`, confirmText: 'بله، غیرفعال کن', icon: 'warning', color: '#ffc107' },
          };

          const label = actionLabels[action] || actionLabels['delete'];

          Swal.fire({
               title: label.title, text: label.text, icon: label.icon,
               showCancelButton: true,
               confirmButtonText: label.confirmText,
               cancelButtonText: 'لغو',
               confirmButtonColor: label.color
          }).then((result) => {
               if (!result.isConfirmed) return;

               $.ajax({
                    url: '/manager/category/bulk-action/',
                    type: 'POST',
                    traditional: true,
                    data: {
                         'ids[]': ids,
                         action: action,
                         csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val()
                    },
                    success: function (response) {
                         if (response.success) {
                              Swal.fire({
                                   icon: 'success', title: 'موفق', text: response.message,
                                   timer: 2000, showConfirmButton: false
                              }).then(() => location.reload());
                         } else {
                              Swal.fire({ icon: 'error', title: 'خطا', text: response.error });
                         }
                    },
                    error: function () {
                         Swal.fire({ icon: 'error', title: 'خطا', text: 'مشکلی در انجام عملیات رخ داد' });
                    }
               });
          });
     });

     // =============================================
     // نمایش زیردسته‌ها
     // =============================================
     $('.view-children').click(function () {
          const id = $(this).data('id');
          const modal = $('#childrenModal');

          modal.find('.modal-body').html(`
               <div class="text-center py-4">
                    <div class="spinner-border text-primary" role="status"></div>
               </div>
          `);
          modal.modal('show');

          $.ajax({
               url: `/manager/category/${id}/children/`,
               type: 'GET',
               success: function (response) {
                    if (!response.success) {
                         modal.find('.modal-body').html(
                              '<div class="text-center py-4 text-danger">خطا در دریافت زیردسته‌ها</div>'
                         );
                         return;
                    }
                    const data = response.data;
                    if (data.length === 0) {
                         modal.find('.modal-body').html(`
                              <div class="text-center py-4">
                                   <i class="fas fa-folder-open fa-3x text-muted mb-3 d-block"></i>
                                   <p class="text-muted">این دسته‌بندی زیردسته‌ای ندارد</p>
                              </div>
                         `);
                         return;
                    }
                    let html = '<ul class="list-group">';
                    data.forEach(function (item) {
                         html += `
                              <li class="list-group-item d-flex align-items-center gap-3">
                                   <span>${item.title}</span>
                                   <code class="ms-auto">${item.slug}</code>
                                   ${item.is_active
                                   ? '<span class="badge bg-success">فعال</span>'
                                   : '<span class="badge bg-danger">غیرفعال</span>'}
                              </li>
                         `;
                    });
                    html += '</ul>';
                    modal.find('.modal-body').html(html);
               },
               error: function () {
                    modal.find('.modal-body').html(
                         '<div class="text-center py-4 text-danger">خطا در بارگذاری زیردسته‌ها</div>'
                    );
               }
          });
     });


     // =============================================
     // حذف خودکار alertها
     // =============================================
     setTimeout(function () {
          $('.alert').fadeOut('slow');
     }, 5000);
});