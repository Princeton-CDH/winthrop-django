$(document).on('select2:select', function(evt) {
	var data = evt.params.data;
	$('#viaf_uri').attr('href', data.id).text(data.id);
});


