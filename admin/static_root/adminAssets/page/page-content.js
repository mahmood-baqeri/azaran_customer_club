$(document).ready(function () {
     var currentPageId = $('input[name="page_id"]').val();
     var csrfToken = $('input[name="csrfmiddlewaretoken"]').val();
     var modal = $('#itemModal');

     // =============================================
     // شمارنده کاراکتر
     // =============================================
     function updateCharCounter(fieldId, maxLength) {
          var value = $(`#${fieldId}`).val() || '';
          var count = value.length;
          var counter = $(`#${fieldId}_counter`);
          if (counter.length) {
               counter.text(`${count}/${maxLength}`);
               counter.removeClass('text-danger text-warning text-success');
               if (count > maxLength) counter.addClass('text-danger');
               else if (count > maxLength * 0.8) counter.addClass('text-warning');
               else counter.addClass('text-success');
          }
     }

     $(document).on('input', '#itemTitle', function () {
          updateCharCounter('itemTitle', 255);
     });

     $(document).on('input', '#itemBody', function () {
          updateCharCounter('itemBody', 10000);
     });

     // =============================================
     // فیلتر آیتم‌ها
     // =============================================
     $('.filter-btn').on('click', function () {
          $('.filter-btn').removeClass('active');
          $(this).addClass('active');
          var filter = $(this).data('filter');
          if (filter === 'all') {
               $('.content-item').show();
          } else {
               $('.content-item').hide();
               $(`.content-item[data-kind="${filter}"]`).show();
          }
     });

     // =============================================
     // افزودن آیتم جدید
     // =============================================
     $('#addItemBtn').on('click', function () {
          $('#itemModalTitle').text('افزودن آیتم جدید');
          $('#itemForm')[0].reset();
          $('#itemId').val('');
          $('#itemKind').val('step');
          $('#itemOrder').val(0);
          $('#itemTitle').val('');
          $('#itemBody').val('');
          $('#itemExtra').val('');
          $('#itemTitle_counter').text('0/255');
          $('#itemBody_counter').text('0/10000');
          modal.modal('show');
     });

     // =============================================
     // ویرایش آیتم
     // =============================================
     $('.edit-item').on('click', function () {
          var itemId = $(this).data('id');
          $('#itemModalTitle').text('ویرایش آیتم');

          $.ajax({
               url: `/manager/page/api/content-item/${itemId}/data/`,
               type: 'GET',
               success: function (response) {
                    if (response.status === 'success') {
                         var item = response.item;
                         $('#itemId').val(item.id);
                         $('#itemKind').val(item.kind);
                         $('#itemOrder').val(item.order);
                         $('#itemTitle').val(item.title || '');
                         $('#itemBody').val(item.body || '');
                         $('#itemExtra').val(JSON.stringify(item.extra || {}, null, 2));
                         updateCharCounter('itemTitle', 255);
                         updateCharCounter('itemBody', 10000);
                         modal.modal('show');
                    }
               },
               error: function () {
                    Swal.fire({ icon: 'error', title: 'خطا', text: 'مشکلی در دریافت اطلاعات رخ داد' });
               }
          });
     });

     // =============================================
     // ذخیره آیتم
     // =============================================
     $('#saveItemBtn').on('click', function () {
          var itemId = $('#itemId').val();
          var formData = new FormData($('#itemForm')[0]);
          formData.append('csrfmiddlewaretoken', csrfToken);

          var title = $('#itemTitle').val();
          if (!title || !title.trim()) {
               Swal.fire({ icon: 'warning', title: 'هشدار', text: 'عنوان الزامی است' });
               return;
          }

          var url = itemId ?
               `/manager/page/api/content-item/edit/${itemId}/` :
               `/manager/page/api/content-item/create/${currentPageId}/`;

          $('#saveItemBtn').prop('disabled', true).html('<i class="fas fa-spinner fa-spin"></i> در حال ذخیره...');

          $.ajax({
               url: url,
               type: 'POST',
               data: formData,
               processData: false,
               contentType: false,
               success: function (response) {
                    if (response.status === 'success') {
                         Swal.fire({
                              icon: 'success',
                              title: 'موفق',
                              text: response.message,
                              timer: 2000,
                              showConfirmButton: false
                         }).then(function () { location.reload(); });
                    } else {
                         Swal.fire({ icon: 'error', title: 'خطا', text: response.message || 'خطا' });
                    }
               },
               error: function (xhr) {
                    var response = xhr.responseJSON;
                    Swal.fire({
                         icon: 'error',
                         title: 'خطا',
                         text: (response && response.message) || 'مشکلی در ذخیره رخ داد'
                    });
               },
               complete: function () {
                    $('#saveItemBtn').prop('disabled', false).html('ذخیره');
               }
          });
     });

     // =============================================
     // حذف آیتم
     // =============================================
     $('.delete-item').on('click', function () {
          var itemId = $(this).data('id');
          var card = $(this).closest('.content-item');

          Swal.fire({
               title: 'حذف آیتم',
               text: 'آیا از حذف این آیتم اطمینان دارید؟',
               icon: 'warning',
               showCancelButton: true,
               confirmButtonText: 'بله، حذف کن',
               cancelButtonText: 'لغو',
               confirmButtonColor: '#dc3545'
          }).then(function (result) {
               if (!result.isConfirmed) return;

               $.ajax({
                    url: `/manager/page/api/content-item/delete/${itemId}/`,
                    type: 'POST',
                    data: { csrfmiddlewaretoken: csrfToken },
                    success: function (response) {
                         if (response.status === 'success') {
                              card.fadeOut(500, function () { $(this).remove(); });
                              Swal.fire({
                                   icon: 'success',
                                   title: 'حذف شد',
                                   text: response.message,
                                   timer: 2000,
                                   showConfirmButton: false
                              });
                         }
                    },
                    error: function () {
                         Swal.fire({ icon: 'error', title: 'خطا', text: 'مشکلی در حذف رخ داد' });
                    }
               });
          });
     });

     // =============================================
     // مرتب‌سازی با Sortable
     // =============================================
     var container = document.getElementById('itemsContainer');
     if (container && typeof Sortable !== 'undefined') {
          new Sortable(container, {
               animation: 150,
               handle: '.item-card',
               onEnd: function () {
                    var items = [];
                    $('.content-item').each(function (index) {
                         items.push({ id: $(this).data('id'), order: index + 1 });
                    });

                    $.ajax({
                         url: '/manager/page/api/content-item/reorder/',
                         type: 'POST',
                         contentType: 'application/json',
                         data: JSON.stringify({ items: items, csrfmiddlewaretoken: csrfToken }),
                         success: function (response) {
                              if (response.status === 'success') {
                                   $('.content-item').each(function (index) {
                                        $(this).find('.badge.bg-secondary').text(`ترتیب: ${index + 1}`);
                                   });
                                   Swal.fire({
                                        icon: 'success',
                                        title: 'موفق',
                                        text: response.message,
                                        timer: 2000,
                                        showConfirmButton: false
                                   });
                              }
                         },
                         error: function () {
                              Swal.fire({ icon: 'error', title: 'خطا', text: 'مشکلی در مرتب‌سازی رخ داد' });
                         }
                    });
               }
          });
     }

     // =============================================
     // اعتبارسنجی فرم مودال
     // =============================================
     $('#itemForm').on('submit', function (e) {
          e.preventDefault();
          $('#saveItemBtn').click();
     });

     // =============================================
     // بستن مودال با Escape
     // =============================================
     $(document).on('keydown', function (e) {
          if (e.key === 'Escape' && modal.hasClass('show')) {
               modal.modal('hide');
          }
     });
});