$(document).ready(function () {

     // =============================================
     //   Select2
     // =============================================
     $('.select2').select2({
          theme: 'bootstrap-5',
          placeholder: 'انتخاب کنید...',
          allowClear: true
     });

     // =============================================
     //  TinyMCE
     // =============================================
     if (typeof tinymce !== 'undefined') {
          tinymce.init({
               selector: '.tinymce',
               height: 400,
               menubar: true,
               plugins: [
                    'advlist', 'autolink', 'lists', 'link', 'image', 'charmap', 'preview',
                    'anchor', 'searchreplace', 'visualblocks', 'code', 'fullscreen',
                    'insertdatetime', 'media', 'table', 'help', 'wordcount'
               ],
               toolbar: 'undo redo | blocks | ' +
                    'bold italic backcolor | alignleft aligncenter ' +
                    'alignright alignjustify | bullist numlist outdent indent | ' +
                    'removeformat | help',
               content_style: 'body { font-family:IRANSans, Arial, sans-serif; font-size:14px; direction:rtl; text-align:right; }',
               directionality: 'rtl',
               language: 'fa',
               language_url: '/static/tinymce/langs/fa.js'
          });
     }

     // =============================================
     //  CKEditor
     // =============================================
     if (typeof CKEDITOR !== 'undefined') {
          $(function () {
               document.querySelectorAll('.online-editor').forEach(function (el) {
                    CKEDITOR.replace(el);
               });
          });
     }
});