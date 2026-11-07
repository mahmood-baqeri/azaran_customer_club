$(document).ready(function() {
	var app = new Mapp({
		element: '#app',
		presets: {
			latlng: {
				lat: 32,
				lng: 52,
			},
			zoom: 6,
		},
		i18n: {
			fa: {
				'marker-title': 'عنوان',
				'marker-description': 'توضیح',
			},
			en: {
				'marker-title': 'Title',
				'marker-description': 'Description',
			},
		},
		locale: 'en',
	});

	app.addLayers();

	var marker = app.addMarker({
		name: 'advanced-marker',
		latlng: {
			lat: 37.375,
			lng: 49.759,
		},
		icon: app.icons.red,
		popup: {
			title: {
				i18n: 'marker-title',
			},
			description: {
				i18n: 'marker-description',
			},
			// custom: 'Custom popup',
			class: 'marker-class',
			open: true,
		},
		pan: false,
		draggable: true,
		history: false,
		on: {
			click: function() {
				console.log('Click callback');
			},
			contextmenu: function() {
				console.log('Contextmenu callback');
			},
		},
	});
});
