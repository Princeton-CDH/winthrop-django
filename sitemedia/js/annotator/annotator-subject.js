/*
annotator subject integration

- adds an subject input field
- display subject name on marginalia item card when present
- stores subject on the annotation
- connects to an autocomplete to use the pre-slugged subject vocabulary
*/

var subject = {
    // render extension to display subject on marginalia item card

    renderExtension: function(annotation, item) {
        // replace existing subject block with updated version
        var subject_div = subject.renderSubject(annotation);
        item.find('.annotator-subject').remove();
        // insert subject (if any) before tags or footer, whichever comes first
        if (subject_div) {
            subject_div.insertAfter(item.find('.text,.annotator-author').last());
        }
        return item;
    },

    renderSubject: function(annotation) {
        var subject_div;
        // display subject name with a label if present in the annotation
        // modeled on marginalia tag renderer
        if (annotation.subject && $.isArray(annotation.subject) && annotation.subject.length > 0) {
            subject_div = $('<div/>').addClass('annotator-subjects').html(function () {
            return '<label>Subject(s):</label>' + $.map(annotation.subject, function (subject) {
              return subject
            }).join(', ');
            });
          }
        return subject_div;
      },

     getEditorExtension: function getEditorExtension(options) {

      // editor extension to make subject editable
     return function editorExtension(e) {
        // The input element added to the Annotator.Editor wrapped in jQuery.
        // Cached to save having to recreate it everytime the editor is displayed.
        var field = null;
        var input = null;


        function updateField(field, annotation) {
            $(field).addClass('subject-lookup');
            // initialize input value & id when annotation.subject is present
            if (annotation.subject){
              subjects = annotation.subject.join(', ')
              input.val(subjects)
            } else {
                input.val('');
            }


            // Function to parse a list of tags and only autocomplete on what's after the
            // comma.
            var parseRecent = function(str) {
              var list = str.split(',');
              var latest = list[list.length - 1]
              return latest.trim()
            }

            // Function that handles passing the query
            var subjAutocompleteSearch = function(request, response) {
              term = parseRecent(request.term);
              $.get(options.subject_autocomplete_url, {q: term},
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

          var selectFunc = function(obj, ui) {
            var val = obj.val()
            if (val.indexOf(',') == -1) {
              val = ui.item.value + ', ';
            } else {
              val = val.replace(/,[^,]+$/, "") + ", " + ui.item.value + ', ';
            }
            obj.val(val);

          }



      // Bind an autocomplete to tags field
          $('.subject-lookup input').autocomplete({
              source: subjAutocompleteSearch,
              select: function(event, ui) {
                selectFunc($(this), ui);
                event.preventDefault();
              },
              focus: function(event, ui) {
                event.preventDefault();
              },
              open: function(event, ui) {
                  // annotator purposely sets the editor at a very high z-index;
                  // set autocomplete still higher so it isn't obscured by annotator buttons
                  $('.ui-autocomplete').css('z-index', $('.annotator-editor').css('z-index') + 1);
              },
          });

        }

        function setSubject(field, annotation) {
            // store subject info on the annotation object
            if (input.val() != '') {
              var subjects = input.val().split(',')
              for (i = 0; i < subjects.length; i++) {
                subjects[i] = subjects[i].trim()
              }
              annotation.subject = subjects
            } else {
                // clear out subject if it was previously set
                annotation.subject = [];
            }
        }

        field = e.addField({
            label: 'Annotation subject(s)',
            type: 'input',
            load: updateField,
            submit: setSubject
        });

        input = $(field).find('input');
    };
}

};
