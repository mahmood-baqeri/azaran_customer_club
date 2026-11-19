// Path: static_root/adminAssets/plugins/fancyuploder/fancy-uploader.js

(function($) {
	//fancyfileuplod
	$('#demo').FancyFileUpload({
	params : {
		 action : 'fileuploader'
		},
		maxfilesize : 1000000
	});
})(jQuery);