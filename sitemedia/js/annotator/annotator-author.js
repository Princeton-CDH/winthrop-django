/*
annotator author integration

- adds an author input field
- display author name on marginalia item card when present
- binds an autocomplete to author input (configured url, intended for
  person lookup)
- stores author name and id on the annotation
*/

var author = {
    // render extension to display author on marginalia item card

    renderExtension: function(annotation, item) {
        // replace existing author block with updated version
        var author_div = author.renderAuthor(annotation);
        item.find('.annotator-author').remove();
        // insert author (if any) before tags or footer, whichever comes first
        if (author_div) {
            author_div.insertBefore(item.find('.annotator-translation,.annotator-anchortext,.annotator-tags,.annotation-footer').first());
        }
        return item;
    },

    renderAuthor: function(annotation) {
        var author_div;
        // display author name with a label if present in the annotation
        if (annotation.author && annotation.author.name) {
            author_div = $('<div/>').addClass('annotator-author').html(
                annotation.author.name
          ).prepend($('<label>Author:</label>'));
        }
        return author_div;
      },

     getEditorExtension: function getEditorExtension(options) {

      // editor extension to make author editable
     return function editorExtension(e) {
        // The input element added to the Annotator.Editor wrapped in jQuery.
        // Cached to save having to recreate it everytime the editor is displayed.
        var field = null;
        var input = null;

        function updateField(field, annotation) {
            $(field).addClass('author-lookup');
            // initialize input value & id when annotation.author is present
            if (annotation.author) {
                input.val(annotation.author.name)
                     .attr('data-author-id', annotation.author.id)
            } else {
                input.val('').removeAttr('data-author-id');
            }

            // configure autocomplete to look up authors from persons in the db
            $('.author-lookup input').autocomplete({
                 source: function(request, response) {
                    $.ajax({
                      dataType: "json",
                      url: options.author_lookup_url,
                      data: { q: request.term, winthrop: true },
                      success: function (data, status, jqXHR) {
                        // convert response into format jquery-ui expects
                        response($.map(data.results, function (value, key) {
                            return {
                                label: value.text,
                                value: value.text,
                                id: value.id
                            };
                        }));
                      }
                    });
                },
                focus: function(event, ui) {
                  event.preventDefault();
                },
                select: function( event, ui ) {
                    // store person id in a data attribute
                    $(event.target).attr('data-author-id', ui.item.id);
                },
                open: function(event, ui) {
                    // annotator purposely sets the editor at a very high z-index;
                    // set autocomplete still higher so it isn't obscured by annotator buttons
                    $('.ui-autocomplete').css('z-index', $('.annotator-editor').css('z-index') + 1);
                },
                position: { my : "right top", at: "right bottom" }
            });
        }

        function setAuthor(field, annotation) {
            // store author info on the annotation object
            if (input.val() != '') {
                annotation.author = {
                    name: input.val(),
                    id: input.attr('data-author-id')
                };
            } else {
                // clear out author if it was previously set
                annotation.author = {};
            }
        }

        field = e.addField({
            label: 'Author',
            load: updateField,
            submit: setAuthor
        });

        input = $(field).find('input');
    };
}

};
