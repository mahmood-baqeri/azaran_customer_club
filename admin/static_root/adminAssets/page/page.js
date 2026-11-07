$(document).ready(function () {

     // =============================================
     // بخش 1: شمارنده کاراکتر — title و summer
     // =============================================
     function createCharCounter(fieldId, maxLength) {
          var field = $(`#${fieldId}`);
          if (field.length === 0) return;

          $(`#${fieldId}_counter`).remove();
          field.after(`<div class="char-counter" id="${fieldId}_counter">0/${maxLength}</div>`);
          updateCharCounter(fieldId, maxLength);
     }

     function updateCharCounter(fieldId, maxLength) {
          var field = $(`#${fieldId}`);
          if (field.length === 0) return;

          var value = field.val() || '';
          var count = value.length;
          var counter = $(`#${fieldId}_counter`);

          if (counter.length === 0) {
               field.after(`<div class="char-counter" id="${fieldId}_counter">${count}/${maxLength}</div>`);
               counter = $(`#${fieldId}_counter`);
          }

          counter.text(`${count}/${maxLength}`);
          counter.removeClass('text-danger text-warning text-success');

          if (count > maxLength) {
               counter.addClass('text-danger');
          } else if (count > maxLength * 0.8) {
               counter.addClass('text-warning');
          } else {
               counter.addClass('text-success');
          }
     }

     function initCharCounters() {
          var fields = [
               { id: 'id_title', max: 120 },
               { id: 'id_summer', max: 500 },
          ];
          fields.forEach(function (item) {
               if ($(`#${item.id}`).length) {
                    createCharCounter(item.id, item.max);
               }
          });
     }

     $(document).on('input', '#id_title, #id_summer', function () {
          var id = $(this).attr('id');
          var max = id === 'id_title' ? 120 : 500;
          if ($(`#${id}_counter`).length) {
               updateCharCounter(id, max);
          }
     });

     setTimeout(initCharCounters, 300);

     // اگر CKEditor روی text فعال بود
     if (typeof CKEDITOR !== 'undefined') {
          CKEDITOR.on('instanceReady', function (evt) {
               var editor = evt.editor;
               var elementId = editor.element.getId();
               if (!elementId) return;
               editor.on('change', function () {
                    setTimeout(function () {
                         var len = editor.getData().length;
                         var counter = $(`#${elementId}_counter`);
                         if (counter.length) {
                              counter.text(`${len}/∞`);
                         }
                    }, 100);
               });
          });
     }

     // =============================================
     // بخش 2: مدیریت گالری
     // =============================================
     function initGalleryManager() {
          var galleryContainer = $('#galleryContainer');
          var galleryInput = $('#id_gallery');
          var galleryImages = [];

          if (!galleryContainer.length && !galleryInput.length) return;

          // ---------- بارگذاری ----------
          function loadExistingImages() {
               try {
                    var raw = galleryInput.val();
                    if (raw) {
                         if (typeof raw === 'string' && raw.trim().startsWith('[')) {
                              galleryImages = JSON.parse(raw);
                         } else if (typeof raw === 'string') {
                              galleryImages = raw.split(',').map(s => s.trim()).filter(Boolean);
                         }
                    }
               } catch (e) {
                    galleryImages = [];
               }
               renderGallery();
          }

          // ---------- رندر ----------
          function renderGallery() {
               galleryContainer.empty();

               if (!galleryImages || galleryImages.length === 0) {
                    galleryContainer.html(`
                         <div class="text-center py-5 text-muted border rounded">
                              <i class="fas fa-images fa-4x mb-3 d-block text-primary"></i>
                              <h5>هیچ تصویری در گالری وجود ندارد</h5>
                              <p class="small">برای آپلود تصاویر، روی دکمه "انتخاب تصاویر" کلیک کنید</p>
                         </div>
                    `);
                    updateGalleryInput();
                    updateGalleryStats();
                    return;
               }

               galleryImages.forEach(function (img, index) {
                    var isImageUrl = img && (img.startsWith('http') || img.startsWith('/media/'));
                    var card = `
                         <div class="col-md-3 col-sm-4 col-6 gallery-item" data-index="${index}">
                              <div class="card h-100 gallery-card">
                                   <div class="position-relative gallery-image-wrapper">
                                        ${isImageUrl ?
                              `<img src="${img}" class="card-img-top gallery-image" alt="تصویر گالری" loading="lazy">` :
                              `<div class="gallery-placeholder bg-light d-flex align-items-center justify-content-center" style="height:150px;">
                                                  <i class="fas fa-file-image fa-3x text-muted"></i>
                                             </div>`
                         }
                                        <div class="gallery-overlay">
                                             <button type="button" class="btn btn-sm btn-danger delete-gallery-image" data-index="${index}">
                                                  <i class="fas fa-trash"></i>
                                             </button>
                                             <button type="button" class="btn btn-sm btn-info view-gallery-image" data-index="${index}">
                                                  <i class="fas fa-eye"></i>
                                             </button>
                                        </div>
                                   </div>
                                   <div class="card-body p-2 text-center">
                                        <small class="text-muted d-block text-truncate">
                                             ${isImageUrl ? img.split('/').pop() : 'تصویر'}
                                        </small>
                                        <div class="btn-group btn-group-sm mt-1" role="group">
                                             <button type="button" class="btn btn-outline-secondary move-up" data-index="${index}" ${index === 0 ? 'disabled' : ''}>
                                                  <i class="fas fa-arrow-up"></i>
                                             </button>
                                             <button type="button" class="btn btn-outline-secondary move-down" data-index="${index}" ${index === galleryImages.length - 1 ? 'disabled' : ''}>
                                                  <i class="fas fa-arrow-down"></i>
                                             </button>
                                        </div>
                                   </div>
                              </div>
                         </div>
                    `;
                    galleryContainer.append(card);
               });

               updateGalleryInput();
               updateGalleryStats();
          }

          function updateGalleryInput() {
               var validImages = galleryImages.filter(img => img && img.trim());
               galleryInput.val(JSON.stringify(validImages));
               $('#galleryCount').text(validImages.length);
          }

          function updateGalleryStats() {
               var count = galleryImages.length;
               $('#galleryStats').html(`
                    <span class="badge bg-primary">${count} تصویر</span>
                    <span class="badge bg-info">${count > 0 ? 'گالری فعال' : 'خالی'}</span>
               `);
          }

          // ---------- آپلود ----------
          function uploadGalleryImages(files) {
               if (!files || files.length === 0) return;

               var formData = new FormData();
               var validFiles = [];

               for (var i = 0; i < files.length; i++) {
                    var file = files[i];
                    if (file.type.startsWith('image/')) {
                         validFiles.push(file);
                         formData.append('gallery_images', file);
                    } else {
                         showNotification(`${file.name} فرمت تصویر ندارد`, 'warning');
                    }
               }

               if (validFiles.length === 0) {
                    showNotification('هیچ فایل تصویری معتبری انتخاب نشد', 'warning');
                    return;
               }

               var progressHtml = `
                    <div class="upload-progress mt-3">
                         <div class="d-flex justify-content-between mb-1">
                              <span>در حال آپلود ${validFiles.length} تصویر...</span>
                              <span class="upload-percentage">0%</span>
                         </div>
                         <div class="progress" style="height: 20px;">
                              <div class="progress-bar progress-bar-striped progress-bar-animated"
                                   role="progressbar" style="width: 0%">0%</div>
                         </div>
                    </div>
               `;

               var progressContainer = $('#uploadProgress');
               progressContainer.html(progressHtml).show();

               $.ajax({
                    url: '/manager/page/upload-gallery/',
                    type: 'POST',
                    data: formData,
                    processData: false,
                    contentType: false,
                    headers: {
                         'X-CSRFToken': $('input[name="csrfmiddlewaretoken"]').val()
                    },
                    xhr: function () {
                         var xhr = new window.XMLHttpRequest();
                         xhr.upload.addEventListener('progress', function (evt) {
                              if (evt.lengthComputable) {
                                   var p = Math.round((evt.loaded / evt.total) * 100);
                                   $('.progress-bar').css('width', p + '%').text(p + '%');
                                   $('.upload-percentage').text(p + '%');
                              }
                         }, false);
                         return xhr;
                    },
                    success: function (response) {
                         if (response.status === 'success') {
                              response.images.forEach(function (img) {
                                   galleryImages.push(img);
                              });
                              renderGallery();
                              showNotification(`${response.images.length} تصویر با موفقیت آپلود شد`, 'success');
                              $('#id_gallery_images').val('');
                              $('#galleryPreview').empty().hide();
                         } else {
                              showNotification(response.message || 'خطا در آپلود', 'danger');
                         }
                    },
                    error: function (xhr, status, error) {
                         showNotification('خطا در آپلود تصاویر: ' + error, 'danger');
                    },
                    complete: function () {
                         progressContainer.hide();
                    }
               });
          }

          function deleteImage(index) {
               Swal.fire({
                    title: 'حذف تصویر',
                    text: 'آیا از حذف این تصویر از گالری اطمینان دارید؟',
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonText: 'بله، حذف کن',
                    cancelButtonText: 'لغو',
                    confirmButtonColor: '#dc3545'
               }).then((result) => {
                    if (result.isConfirmed) {
                         var imageUrl = galleryImages[index];
                         galleryImages.splice(index, 1);
                         renderGallery();

                         $.ajax({
                              url: '/manager/page/delete-gallery-image/',
                              type: 'POST',
                              data: {
                                   image: imageUrl,
                                   csrfmiddlewaretoken: $('input[name="csrfmiddlewaretoken"]').val()
                              },
                              success: function () {
                                   showNotification('تصویر با موفقیت حذف شد', 'success');
                              },
                              error: function () {
                                   showNotification('تصویر از گالری حذف شد', 'info');
                              }
                         });
                    }
               });
          }

          function viewImage(index) {
               var img = galleryImages[index];
               if (!img) return;
               var modal = $('#imagePreviewModal');
               modal.find('.modal-body').html(`<img src="${img}" class="img-fluid" alt="تصویر گالری">`);
               modal.modal('show');
          }

          function moveImage(index, direction) {
               var newIndex = direction === 'up' ? index - 1 : index + 1;
               if (newIndex < 0 || newIndex >= galleryImages.length) return;
               var temp = galleryImages[index];
               galleryImages[index] = galleryImages[newIndex];
               galleryImages[newIndex] = temp;
               renderGallery();
               showNotification('ترتیب تصاویر تغییر کرد', 'info');
          }

          function showNotification(message, type = 'info') {
               var alertClass = type === 'success' ? 'alert-success' :
                    type === 'danger' ? 'alert-danger' :
                         type === 'warning' ? 'alert-warning' : 'alert-info';
               var iconClass = type === 'success' ? 'check-circle' :
                    type === 'danger' ? 'exclamation-circle' :
                         type === 'warning' ? 'exclamation-triangle' : 'info-circle';

               var notification = $(`
                    <div class="alert ${alertClass} alert-dismissible fade show gallery-notification" role="alert">
                         <i class="fas fa-${iconClass} me-2"></i>
                         ${message}
                         <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                    </div>
               `);

               $('#galleryNotification').append(notification);
               setTimeout(function () {
                    notification.fadeOut(500, function () { $(this).remove(); });
               }, 5000);
          }

          // ---------- رویدادها ----------
          $('#id_gallery_images').on('change', function () {
               var files = $(this)[0].files;
               if (files.length > 0) {
                    var previewContainer = $('#galleryPreview');
                    previewContainer.empty().show();
                    Array.from(files).slice(0, 6).forEach(function (file) {
                         var reader = new FileReader();
                         reader.onload = function (e) {
                              previewContainer.append(`
                                   <div class="col-md-2 col-sm-3 col-4">
                                        <div class="card mb-2">
                                             <img src="${e.target.result}" class="card-img-top" style="height: 80px; object-fit: cover;">
                                             <div class="card-body p-1 text-center small text-truncate">${file.name}</div>
                                        </div>
                                   </div>
                              `);
                         };
                         reader.readAsDataURL(file);
                    });
                    uploadGalleryImages(files);
               }
          });

          galleryContainer.on('click', '.delete-gallery-image', function () {
               deleteImage($(this).data('index'));
          });

          galleryContainer.on('click', '.view-gallery-image', function () {
               viewImage($(this).data('index'));
          });

          galleryContainer.on('click', '.move-up', function () {
               moveImage($(this).data('index'), 'up');
          });

          galleryContainer.on('click', '.move-down', function () {
               moveImage($(this).data('index'), 'down');
          });

          $('#clearGallery').on('click', function () {
               if (galleryImages.length === 0) {
                    showNotification('گالری خالی است', 'warning');
                    return;
               }
               Swal.fire({
                    title: 'پاک کردن گالری',
                    text: `آیا از حذف تمام ${galleryImages.length} تصویر گالری اطمینان دارید؟`,
                    icon: 'warning',
                    showCancelButton: true,
                    confirmButtonText: 'بله، پاک کن',
                    cancelButtonText: 'لغو',
                    confirmButtonColor: '#dc3545'
               }).then((result) => {
                    if (result.isConfirmed) {
                         galleryImages = [];
                         renderGallery();
                         showNotification('گالری پاک شد', 'success');
                    }
               });
          });

          // Drag & Drop
          var dropZone = $('#galleryDropZone');
          if (dropZone.length) {
               dropZone.on('dragover', function (e) {
                    e.preventDefault();
                    $(this).addClass('dragover');
               });
               dropZone.on('dragleave', function (e) {
                    e.preventDefault();
                    $(this).removeClass('dragover');
               });
               dropZone.on('drop', function (e) {
                    e.preventDefault();
                    $(this).removeClass('dragover');
                    var files = e.originalEvent.dataTransfer.files;
                    if (files.length > 0) uploadGalleryImages(files);
               });
          }

          loadExistingImages();
     }

     initGalleryManager();

     // =============================================
     // بخش 3: انتخاب همه / لغو انتخاب
     // =============================================
     $('#checkAll').change(function () {
          $('.page-checkbox').prop('checked', $(this).prop('checked'));
          updateSelectedCount();
     });

     $('#selectAll').click(function () {
          $('.page-checkbox').prop('checked', true);
          $('#checkAll').prop('checked', true);
          updateSelectedCount();
     });

     $('#deselectAll').click(function () {
          $('.page-checkbox').prop('checked', false);
          $('#checkAll').prop('checked', false);
          updateSelectedCount();
     });

     $('.page-checkbox').change(updateSelectedCount);

     function updateSelectedCount() {
          const count = $('.page-checkbox:checked').length;
          $('#selectedCount').text(count + ' انتخاب شده');
          $('#checkAll').prop(
               'checked',
               $('.page-checkbox:checked').length === $('.page-checkbox').length && $('.page-checkbox').length > 0
          );
     }

     // =============================================
     // بخش 4: toggle وضعیت
     // =============================================
     $('.status-badge').click(function () {
          const $badge = $(this);
          const id = $badge.data('id');

          Swal.fire({
               title: 'تغییر وضعیت',
               text: 'آیا از تغییر وضعیت این صفحه اطمینان دارید؟',
               icon: 'question',
               showCancelButton: true,
               confirmButtonText: 'بله، تغییر کن',
               cancelButtonText: 'لغو',
          }).then((result) => {
               if (!result.isConfirmed) return;

               $.ajax({
                    url: '/manager/page/toggle-status/',
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
                         Swal.fire({ icon: 'error', title: 'خطا', text: 'مشکلی رخ داد' });
                    }
               });
          });
     });

     // =============================================
     // بخش 5: حذف صفحه
     // =============================================
     $('.delete-page').click(function () {
          const id = $(this).data('id');
          const row = $(this).closest('tr');

          Swal.fire({
               title: 'حذف صفحه',
               text: 'آیا از حذف این صفحه اطمینان دارید؟ این عملیات غیرقابل بازگشت است.',
               icon: 'warning',
               showCancelButton: true,
               confirmButtonText: 'بله، حذف کن',
               cancelButtonText: 'لغو',
               confirmButtonColor: '#dc3545',
          }).then((result) => {
               if (!result.isConfirmed) return;

               $.ajax({
                    url: '/manager/page/delete/',
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
                                   text: response.message || 'صفحه حذف شد',
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
     // بخش 6: عملیات دسته‌جمعی
     // =============================================
     $('.bulk-action').click(function () {
          const action = $(this).data('action');
          const ids = $('.page-checkbox:checked').map(function () {
               return $(this).val();
          }).get();

          if (ids.length === 0) {
               Swal.fire({ icon: 'warning', title: 'هشدار', text: 'لطفاً حداقل یک صفحه را انتخاب کنید' });
               return;
          }

          const actionLabels = {
               'delete': { title: 'حذف دسته‌جمعی', text: `${ids.length} صفحه حذف خواهند شد`, confirmText: 'بله، حذف کن', icon: 'warning', color: '#dc3545' },
               'activate': { title: 'فعال‌سازی دسته‌جمعی', text: `${ids.length} صفحه فعال خواهند شد`, confirmText: 'بله، فعال کن', icon: 'success', color: '#28a745' },
               'deactivate': { title: 'غیرفعال‌سازی دسته‌جمعی', text: `${ids.length} صفحه غیرفعال خواهند شد`, confirmText: 'بله، غیرفعال کن', icon: 'warning', color: '#ffc107' },
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
                    url: '/manager/page/bulk-action/',
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
     // بخش 7: نمایش آمار (بدون SEO)
     // =============================================
     $('#showStats').click(function () {
          const modal = $('#statsModal');
          modal.find('.modal-body').html(`
               <div class="text-center py-4">
                    <div class="spinner-border text-primary" role="status"></div>
               </div>
          `);
          modal.modal('show');

          $.ajax({
               url: '/manager/page/stats/',
               type: 'GET',
               success: function (response) {
                    if (!response.success) return;
                    const data = response.data;

                    let html = `
                         <div class="row g-3">
                              <div class="col-md-4">
                                   <div class="card bg-primary text-white">
                                        <div class="card-body">
                                             <h6 class="card-title">کل صفحات</h6>
                                             <h3 class="mb-0">${data.total}</h3>
                                        </div>
                                   </div>
                              </div>
                              <div class="col-md-4">
                                   <div class="card bg-success text-white">
                                        <div class="card-body">
                                             <h6 class="card-title">فعال</h6>
                                             <h3 class="mb-0">${data.active}</h3>
                                        </div>
                                   </div>
                              </div>
                              <div class="col-md-4">
                                   <div class="card bg-danger text-white">
                                        <div class="card-body">
                                             <h6 class="card-title">غیرفعال</h6>
                                             <h3 class="mb-0">${data.inactive}</h3>
                                        </div>
                                   </div>
                              </div>
                         </div>
                    `;

                    if (data.by_type && Object.keys(data.by_type).length) {
                         html += `
                              <div class="row mt-3">
                                   <div class="col-12">
                                        <div class="card">
                                             <div class="card-body">
                                                  <h6 class="card-title">آمار بر اساس نوع</h6>
                                                  <div class="row">
                         `;
                         for (const [type, count] of Object.entries(data.by_type)) {
                              html += `
                                   <div class="col-md-3">
                                        <div class="border rounded p-2 text-center">
                                             <strong>${type}</strong>
                                             <span class="badge bg-primary ms-2">${count}</span>
                                        </div>
                                   </div>
                              `;
                         }
                         html += `</div></div></div></div></div>`;
                    }

                    if (data.by_category && Object.keys(data.by_category).length) {
                         html += `
                              <div class="row mt-3">
                                   <div class="col-12">
                                        <div class="card">
                                             <div class="card-body">
                                                  <h6 class="card-title">آمار بر اساس دسته‌بندی</h6>
                                                  <div class="row">
                         `;
                         for (const [cat, count] of Object.entries(data.by_category)) {
                              html += `
                                   <div class="col-md-3">
                                        <div class="border rounded p-2 text-center">
                                             <strong>${cat}</strong>
                                             <span class="badge bg-info ms-2">${count}</span>
                                        </div>
                                   </div>
                              `;
                         }
                         html += `</div></div></div></div></div>`;
                    }

                    modal.find('.modal-body').html(html);
               },
               error: function () {
                    modal.find('.modal-body').html(`
                         <div class="text-center py-4 text-danger">
                              <i class="fas fa-exclamation-circle fa-3x mb-3 d-block"></i>
                              <p>مشکلی در بارگذاری آمار رخ داد</p>
                         </div>
                    `);
               }
          });
     });

     // =============================================
     // بخش 8: حذف خودکار پیام‌ها
     // =============================================
     setTimeout(function () {
          $('.alert').fadeOut('slow');
     }, 5000);
});