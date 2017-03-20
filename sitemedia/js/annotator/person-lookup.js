/**
Annotator module for person lookup.

- editor extension adds an autocomplete field to search for
  a person in the database and add them to the annotation.
- marginalia render extension to display person
- uses select2.js autocomplete for editor input field

*/
var person_lookup = {

    renderExtension: function(annotation, item) {
        // replace existing related pages block with updated version
        var person = person.renderPerson(annotation);
        item.find('.annotator-author').remove();
        // insert person (if any) before tags or footer, whichever comes first
        if (person && person.length) {
            person.insertBefore(item.find('.annotator-tags,.annotation-footer').first());
        }
        return item;
    },

    renderPerson: function(annotation) {
        var person = '';
        if (annotation.person) {
          person = $('<div/>').addClass('annotator-author').html(function () {
            return 'Author: ' + annotation.person;  // name/id?
          });
        }
        return person;
      },

    getEditorExtension: function getEditorExtension(options) {
        // define a new editor function, with the configured
        // search url to find pages

        return function editorExtension(editor) {
            // The input element added to the Annotator.Editor wrapped in jQuery.
            // Cached to save having to recreate it everytime the editor is displayed.
            var field = null;
            var input = null;

/*            function updateField(field, annotation) {
                // convert list of related uris stored in the annnotation
                // into a comma-separated list for the form
                var value = '';
                if (annotation.person && annotation.related_pages.length) {
                    value = annotation.related_pages.join(', ') + ', ';
                }
                input.val(value);
            }
*/
           function setRelatedPages(field, annotation) {
                // split comma-separated uris into an array,
                // removing any empty or duplicated values
                annotation.related_pages = related_pages.split(input.val()).filter(function(el, index, arr){
                    return el !== '' && index === arr.indexOf(el);
                });
            }

            field = editor.addField({
                label: _t('Add author') + '\u2026',
                load: updateField,
                submit: setRelatedPages,
                type: 'textarea'
            });


            input = $(field).find(':input');
            input.addClass('related-pages');

            /* enable autocomplete on related pages input */
            $(".related-pages").relatedPageComplete({
                minLength: 2,
                source: function(request, response) {
                    $.getJSON(options.search_url, {
                        keyword: related_pages.extractLast(request.term)
                    }, response );
                },
                open: function(event, ui) {
                    /* annotator purposely sets the editor at a higher z-index
                    than anything else on the page; make sure the autocomplete
                    menu is still higher so it isn't obscured by annotator buttons */
                    $('.ui-autocomplete').zIndex($(event.target).zIndex() + 1);
                },
                select: function( event, ui ) {
                  /* multi-valued input */
                  var terms = related_pages.split(this.value);
                  // remove the current input (search term)
                  terms.pop();
                  // add the selected item
                  terms.push(ui.item.uri);
                  // add placeholder to get the comma-and-space at the end
                  terms.push("");
                  this.value = terms.join(", ");
                  return false;
                },
                focus: function() {
                    // prevent value inserted on focus
                    return false;
                },
                change: function(event, ui) {
                    // If ui is not set, value was entered directly without
                    // selecting from the list.
                    // Search to confirm it's a valid page ark for this volume
                    if (ui.item == null) {
                        var terms = related_pages.split(this.value);
                        var last_term = terms.pop();
                        $.getJSON(options.search_url, {
                            keyword: last_term
                        }, function(data) {
                            if (data.length == 1 && last_term == data[0].uri) {
                                // nothing to do - input value is valid
                            } else {
                                // no match - term is not a valid page ark
                                // update autocomplete value without the last term

                                // add placeholder to get the comma-and-space at the end
                                terms.push("");
                                this.value = terms.join(", ");
                                // also update input for display to the user
                                $('.related-pages').val(this.value);
                            }
                        });
                    }
                    return false;
                },
                position: { my : "right top", at: "right bottom" }
            });


        }
    }
};


/* extend autocomplete for custom render item method */
$.widget("readux.relatedPageComplete", $.ui.autocomplete, {
    _renderItem: function(ul, item) {
         var li = $("<li>")
            .attr("data-value", item.uri)
            .append('<img class="pull-right" src="' + item.thumbnail + '"/>')
            .append('<h3>' + item.label + '</h3>');
        if (item.highlights && item.highlights.length > 0) {
            li.append('<p>...' + item.highlights[0] + '...</p>');
        }
        li.append('<p class="text-muted small">' + item.uri + '</p>');

        return li.appendTo(ul);
    },
});


