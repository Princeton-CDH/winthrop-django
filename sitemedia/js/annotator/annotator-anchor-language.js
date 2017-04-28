/*
annotator annotation-language integration

- adds an anchor-anchorLanguage input field
- display anchorLanguage name on marginalia item card when present
- stores anchorLanguage on the annotation
- connects to an autocomplete to use the pre-slugged anchorLanguage vocabulary
*/





var anchorLanguage = {
    // render extension to display anchorLanguage on marginalia item card

    renderExtension: function(annotation, item) {
        // replace existing anchorLanguage block with updated version
        var anchorLanguage_div = anchorLanguage.renderAnchorLanguage(annotation);
        item.find('.annotator-anchorLanguage').remove();
        // insert anchorLanguage (if any) before tags or footer, whichever comes first
        if (anchorLanguage_div) {
            anchorLanguage_div.insertAfter(item.find('.annotator-languages,.annotator-anchortext,.annotator-author').last());
        }
        return item;
    },

    renderAnchorLanguage: function(annotation) {
        var anchorLanguage_div;
        // display anchorLanguage name with a label if present in the annotation
        // modeled on marginalia tag renderer
        if (annotation.anchorLanguage && $.isArray(annotation.anchorLanguage) && annotation.anchorLanguage.length > 0) {
            anchorLanguage_div = $('<div/>').addClass('annotator-anchorLanguage').html(function () {
            return '<label>Anchor text language(s):</label>' + $.map(annotation.anchorLanguage, function (anchorLanguage) {
              return anchorLanguage
            }).join(', ');
            });
          }
        return anchorLanguage_div;
      },

     getEditorExtension: function getEditorExtension(options) {

      // editor extension to make anchorLanguage editable
     return function editorExtension(e) {
        // The input element added to the Annotator.Editor wrapped in jQuery.
        // Cached to save having to recreate it everytime the editor is displayed.
        var field = null;
        var input = null;


        function updateField(field, annotation) {
            $(field).addClass('anchorLanguage-lookup');
            // initialize input value & id when annotation.anchorLanguage is present
            if (annotation.anchorLanguage){
              anchorLanguages = annotation.anchorLanguage.join(', ')
              input.val(anchorLanguages)
            } else {
                input.val('');
            }


            // Function to parse a list of tags and only autocomplete on what's after the
            // comma.
            var parseRecentLang = function(str) {
              var list = str.split(',');
              var latest = list[list.length - 1]
              return latest.trim()
            }

            // Function that handles passing the query
            var langAutocompleteSearch = function(request, response) {
              term = parseRecentLang(request.term);
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
          $('.anchorLanguage-lookup input').autocomplete({
              source: langAutocompleteSearch,
              focus: function(event, ui) {
                event.preventDefault();
              },
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

        function setAnchorLanguage(field, annotation) {
            // store anchorLanguage info on the annotation object
            if (input.val() != '') {
              var anchorLanguages = input.val().split(',')
              for (i = 0; i < anchorLanguages.length; i++) {
                anchorLanguages[i] = anchorLanguages[i].trim()
              }
              annotation.anchorLanguage = anchorLanguages
            } else {
                // clear out anchorLanguage if it was previously set
                annotation.anchorLanguage = [];
            }
        }

        field = e.addField({
            label: 'Anchor text language(s)',
            type: 'input',
            load: updateField,
            submit: setAnchorLanguage
        });

        input = $(field).find('input');
    };
}

};
