/*
annotator language integration

- adds an language input field
- display language name on marginalia item card when present
- stores language on the annotation
*/





var language = {
    // render extension to display language on marginalia item card

    renderExtension: function(annotation, item) {
        // replace existing language block with updated version
        var language_div = language.renderLanguage(annotation);
        item.find('.annotator-language').remove();
        // insert language (if any) before tags or footer, whichever comes first
        if (language_div) {
            language_div.insertAfter(item.find('.text,.annotator-author').last());
        }
        return item;
    },

    renderLanguage: function(annotation) {
        var language_div;
        // display language name with a label if present in the annotation
        // modeled on marginalia tag renderer
        if (annotation.language && $.isArray(annotation.language)) {
            language_div = $('<div/>').addClass('annotator-languages').html(function () {
            return '<label>Languages:</label>' + $.map(annotation.language, function (language) {
              return annotator.util.escapeHtml(language)
              }).join(', ');
            });
          }
        return language_div;
      },

     getEditorExtension: function getEditorExtension(options) {

      // editor extension to make language editable
     return function editorExtension(e) {
        // The input element added to the Annotator.Editor wrapped in jQuery.
        // Cached to save having to recreate it everytime the editor is displayed.
        var field = null;
        var input = null;


        function updateField(field, annotation) {
            $(field).addClass('language-lookup');
            // initialize input value & id when annotation.language is present
            if (annotation.language){
              languages = annotation.language.join(', ')
              input.val(languages)
            } else {
                input.val('');
            }


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
              $.get(options.language_autocomplete_url, {q: term},
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
          $('.language-lookup input').autocomplete({
              source: tagAutocompleteSearch,
              select: function(event, ui) {
                var val = $(this).val()
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

        }

        function setLanguage(field, annotation) {
            // store language info on the annotation object
            if (input.val() != '') {
              var languages = input.val().split(',')
              for (i = 0; i < languages.length; i++) {
                languages[i] = languages[i].trim()
              }
              annotation.language = languages
            } else {
                // clear out language if it was previously set
                annotation.language = [];
            }
        }

        field = e.addField({
            label: 'Annotation language(s)',
            type: 'input',
            load: updateField,
            submit: setLanguage
        });

        input = $(field).find('input');
    };
}

};
