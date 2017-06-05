/* Integration for binding jQuery autocomplete to tags field from marginalia

- For now, leaving it independent of the tags logic in Marginalia since use case may change.
- Parses a string of comma separated tags and handles the lookup to an autocomplete
- bindTagAutocomplete function takes two arguments:
    1. autocomplete_url - an autocomplete lookup
    2. id_string - a jQuery compatibile selector

- TODO: Figure out how to refactor as marginalia develop continues

*/

var bindTagAutocomplete = function(autocomplete_url, id_string) {
  // Function to parse a list of tags and only autocomplete on what's after the
  // comma.
  var parseRecentTag = function(str) {
    var list = str.split(',');
    var latest = list[list.length - 1]
    return latest.trim()
  }

  // Function that handles passing the query
  var tagAutocompleteSearch = function(request, response) {
    term = parseRecentTag(request.term);
    $.get(autocomplete_url, {q: term},
        function(data) {
          // convert response into format jquery-ui expects
          response($.map(data.results, function (value, key) {
              return {
                  label: value.text,
                  value: value.text,
                  id: value.id
              };
          }));
        });
    }

  // Bind an autocomplete to tags field
      $(id_string).autocomplete({
          source: tagAutocompleteSearch,
          minLength: 0,
          focus: function(event, ui) {
            event.preventDefault();
          },
          select: function(event, ui) {
            var val = $('#annotator-field-1').val()
            if (val.indexOf(',') == -1) {
              val = ui.item.value + ', ';
            } else {
              val = val.replace(/,[^,]+$/, "") + ", " + ui.item.value + ', ';
            }
            $(this).val(val);
            // Stop the default event from firing because we're
            // handling the setting
            event.preventDefault();
          },
          open: function(event, ui) {
              // annotator purposely sets the editor at a very high z-index;
              // set autocomplete still higher so it isn't obscured by annotator buttons
              $('.ui-autocomplete').css('z-index', $('.annotator-editor').css('z-index') + 1);
          },
      });

      $(id_string).bind('focus', function () {
        $(this).autocomplete("search");
}
