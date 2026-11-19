// Path: static_root/adminAssets/plugins/darggable/darggable.js

$(function () {
	// ______________Dragable cards
	$(".sortable").sortable({
		connectWith: '.sortable',
		items: '.card-draggable',
		revert: true,
		placeholder: 'card-draggable-placeholder',
		forcePlaceholderSize: true,
		opacity: 0.77,
		cursor: 'move'
	});
});