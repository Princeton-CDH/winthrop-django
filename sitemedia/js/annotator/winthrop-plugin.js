/*
Winthrop Annotator Plugin
- Requirements: jQuery, annotator.js 2.0+, marginalia
- Create object 'winthrop' with methods to create a rende rextension
and editor extension for Winthrop Family on the Page Project fields
- conf objects should specify the following properties: name, label, and type (if list),
along with an autocompleteUrl, fieldType ('textarea', 'input' (default))
*/

var winthrop = {
  // Factory function for creating a render extension for all fields
  // Takes an array of configuration objects, in order of display
  makeRenderExtension: function(confs) {

    // Renders the field for display on side card
    function renderField(fieldValue, conf) {
      var div = null;
      // Just in case, to catch an actual 0 if this code
      // is ever re-used
      if (typeof fieldValue != 'undefined' && !$.isEmptyObject(fieldValue)) {
        // split arrays into a comma delimited string
        if ($.isArray(fieldValue)) {
          div = $('<div/>').addClass('annotator-' + conf.name).html(function() {
            return '<label class="field-label">' + conf.label + '</label>' + $.map(fieldValue, function(value) {
              return value
            }).join(', ');
          });
        } else {
          // otherwise return the field value
          div = $('<div/>').addClass('annotator-' + conf.name).html(
            fieldValue
          ).prepend($('<label class="field-label">' + conf.label + '</label>'));
        }
      }
      return div;
    }
    // rendered function that iterates over confs array
    return function(annotation, item) {
      var previousClass = '.text'
      for (i in confs) {
        // Invoke renderField with options as passed to function
        var div = renderField(annotation[confs[i].name], confs[i]);
        var divClass = '.annotator-' + confs[i].name
        item.find(divClass).remove();
        if (div != null) {
          div.insertAfter(item.find(previousClass));
          previousClass = divClass;
        }
      }

      var annotationText = item.find('.text').children();
      if (annotationText.text() == 'No comment') {
        annotationText.text('No annotation text');
      }

      return item;
    }
  },

  // Factory function for extension fieldNames
  // Takes an array of FieldConfig objects, in order of display
  makeEditorExtension: function(confs) {

    // Generic functionality for field setter
    function makeSetField(conf, input) {
      return function(field, annotation) {
        // set the annotation object with an empty string
        annotation[conf.name] = '';
        if (input.val() != '') {
          if (conf.type == 'list') {
            values = input.val().split(',');
            for (i in values) {
              // set an array of values, trimming any stray commas
              values[i] = values[i].trim().replace(/(^,)|(,$)/g, "");
            }
            annotation[conf.name] = values
          } else {
            annotation[conf.name] = input.val();
          }
        }
      }
    }

    // Generic functionality for updating a field
    function makeUpdateField(conf, input) {
      return function(field, annotation) {
        // Give it a class to mark it as that field based on name property
        $(field).addClass(conf.name + '-lookup');
        // If the property exists on the object and isn't a falsy value
        // use the type property to determine how to set the field values
        if (annotation[conf.name] || annotation[conf.name == 0]) {
          if (conf.type == 'list') {
            input.val(annotation[conf.name].join(', '));
          } else {
            input.val(annotation[conf.name]);
          }
        }
        // otherwise, set it to an empty string
        else {
          input.val('');
        }
      }
    }
    // The input element added to the Annotator.Editor wrapped in jQuery.
    // Cached to save having to recreate it everytime the editor is displayed.
    return function editorExtension(e) {
      var field = null;
      var input = null;

      for (var i in confs) {
        // loop through all the fields and add them to e
        var type = confs[i].size ? confs[i].size : 'input'
        field = e.addField({
          // This is properly *placeholder*, so setting is as such
          // using label as fallback
          label: confs[i].placeholder ? confs[i].placeholder : confs[i].label,
          type: type
        });
        input = $(field).find(type);
        var fields = e.fields
        // Add the load and submit functions now that
        // we have an input DOM object
        // field will always be last added to array
        fields[fields.length-1].load = makeUpdateField(confs[i], input);
        fields[fields.length-1].submit = makeSetField(confs[i], input);

        // Give a label field to the input too
        input.parent().prepend('<label class="field-label">'+confs[i].label+'</label>');

        /*
        The following code does the following:
          1) Provides utility functions for parsing a list of tags into an array
          2) Binds an autocomplete for all of the tag lists and provides
            an alternate for the author field specifically
          3)
        */
        // Function to parse the most recent tag
        function parseRecent(str) {
          var list = str.split(',');
          var latest = list[list.length - 1]
          return latest.trim()
        }

        function makeSearchFunction(conf) {
        // Configure the ajax query using GET shorthand
          return function(request, response) {
            term = parseRecent(request.term);
            // autoCompleteUrl from conf function
            $.get(conf.autocompleteUrl, {
                q: term
              },
              function(data) {
                // convert response into format jquery-ui expects
                response($.map(data.results, function(value, key) {
                  return {
                    label: value.text,
                    value: value.text,
                    id: value.id
                  };
                }));
              });
          }
      }

      // Function that triggers on select to add an item to a list
      function SelectFunc(obj, ui) {
          var val = obj.val();
          // comma list style handling
            if (val.indexOf(',') == -1) {
              val = ui.item.value + ', ';
            } else {
              val = val.replace(/,[^,]+$/, "") + ", " + ui.item.value + ', ';
            }
        // Regardless, set the object
        obj.val(val);
      }

        // Actually configure and bind the autocomplete
        if (confs[i].autocompleteUrl) {
          if (confs[i].name != 'author') {
            input.autocomplete({
              source: makeSearchFunction(confs[i]),
              minLength: 0,
              select: function(event, ui) {
                SelectFunc($(this), ui);
                event.preventDefault();
              },
              focus: function(event, ui) {
                event.preventDefault();
              },
              open: function(event, ui) {
                // annotator purposely sets the editor at a very high z-index;
                // set autocomplete still higher so it isn't obscured by annotator buttons
                $('.ui-autocomplete')
                  .css('z-index', $('.annotator-editor').css('z-index') + 1);
              },
            });
          }
          // Special handling for author as the odd field out
          // since it's not a parsed list
          else {
            input.autocomplete({
              source: makeSearchFunction(confs[i]),
              minLength: 0,
              focus: function(event, ui) {
                event.preventDefault();
              },
              open: function(event, ui) {
                // annotator purposely sets the editor at a very high z-index;
                // set autocomplete still higher so it isn't obscured by annotator buttons
                $('.ui-autocomplete')
                  .css('z-index', $('.annotator-editor').css('z-index') + 1);
              },
            });
          }
          // Bind a element to make the autocomplete window pop up on focus
          input.bind('focus', function () {
            $(this).autocomplete("search");
          })
      }

      }
    }

    // makeEditorExtension wrapper end brance
  }
  // winthrop wrapper end brace
}

/*
Winthrop Annotator Override
-A simple jQuery shim to fix the text on the 'Comment' box to something more
sensible
*/
function fixComment(field) {
  // field - any valid jQuery selector for the annotation text field
  $(field).attr('placeholder', 'Annotation text...');
}
