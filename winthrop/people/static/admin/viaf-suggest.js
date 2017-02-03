$(document).on('select2:select', function(evt) {
	var data = evt.params.data;
	$('input[name="sort_name"]').val(data.authorized_name);
	$('input[name="viaf_id"]').val(data.id);
	$('input[name="birth"]').val(data.birth);
	$('input[name="death"]').val(data.death);
	$('select[name="authorized_name"]').val(data.authorized_name);
});


