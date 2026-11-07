/**
 * @license Copyright (c) 2003-2019, CKSource - Frederico Knabben. All rights reserved.
 * For licensing, see https://ckeditor.com/legal/ckeditor-oss-license
 */

CKEDITOR.editorConfig = function (config) {
    config.language = 'fa';
    config.uiColor = '#09a1bb50';
    config.height = 400;
    config.toolbarCanCollapse = true;
    config.extraPlugins = 'wordcount,notification';
    config.toolbar = [
        ['Maximize', 'Source', 'Styles','Format','Font','FontSize'],  '/',
        ['TextColor', 'BGColor'], ['Bold', 'Italic', 'Underline', 'Strike', 'RemoveFormat'], ['Subscript', 'Superscript'],
        ['JustifyLeft', 'JustifyRight', 'JustifyCenter', 'JustifyBlock'], ['NumberedList', 'BulletedList'], ['Outdent', 'Indent', 'Blockquote'], ['Table', 'HorizontalRule'], ['Link', 'Unlink', 'Image'],
        ['Cut', 'Copy', 'Paste', 'PasteText', 'PasteFromWord'], ['Find', 'Replace', 'Print', '-', 'Undo', 'Redo','-' ,'Smiley'],
    ];
}

