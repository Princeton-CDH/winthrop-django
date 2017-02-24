$(document).on('select2:select', function(evt) {
	var data = evt.params.data;
	$('#viaf_uri').attr('href', data.id).text(data.id);
	// Clear birth and death so that VIAF record can set them
	$('#id_birth').val('');
	$('#id_death').val('');
});
