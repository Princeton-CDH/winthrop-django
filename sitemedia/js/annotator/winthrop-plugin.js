/*
Winthrop Annotator Plugin
- Requiresments: jQuery, annotator.js 2.0+, marginalia
- add object 'winthrop' with methods to create a renderextension
and editor extension for Winthrop Family on the Page Project
*/

var winthrop = {
  // Factory function for creating a render extension for all fields
  // Takes an array of configuration objects, in order of display
  makeRenderExtension: function(confs) {
    // TODO: add renderField and make this work
    return function(annotation, item) {
      for (i = 0; i < len(confs); i++) {
        // Invoke renderField with options as passed to function
        var div = renderField(annotation[confs[i].name], confs[i]);
        item.find('.annotator-' + confs[i].name).remove();
        if (div != null) {
          div.insertAfter(item)
            .find('.text', +(i == 0 ? confs[i].name : confs[i - 1].name).last())
        }
      }
      return item;
    }
  },

  // Factory function for extension fieldNames
  // Takes an array of FieldConfig objects, in order of display
  makeEditorExtension: function(confs) {
    // The input element added to the Annotator.Editor wrapped in jQuery.
    // Cached to save having to recreate it everytime the editor is displayed.
    return function editorExtension(e) {
      var field = null;
      var input = null;

      for (i = 0; i < confs.length; i++) {
        // loop through all the fields and add them to e

        // Generic functionality for updating a field
        function makeUpdateField(confs) {
          return function(field, annotation) {
            // Give it a class to mark it as that field based on name property
            var confs = field.confs
            $(field).addClass(confs[i].name + '-lookup');
            // If the property exists on the object and isn't a falsy value
            // use the type property to determine how to set the field values
            if (annotation[confs[i].name]) {
              if (anotation.type = 'list') {
                input.val(annotation[confs[i].name].join(', '))
              } else {
                input.val(annotation[confs[i].name]);
              }
            }
            // otherwise, set it to an empty string
            else {
              input.val('');
            }
          }
        }

        // Generic functionality for field setter
        function makeSetField(confs) {
          return function(field, annotation) {
            // variable scoped for this function
            // avoids getting tangled in flow control below
            var value = null;
            // set the annotation object with an empty string
            annotation[confs[i].name] = '';
            //
            if (input.val() != '') {
              if (confs[i].type == 'list') {
                value = input.val().split(',');
                for (i = 0; i < value.length; i++) {
                  // set an array of values, trimming any stray commas
                  value[i] = value[i].trim().replace(/(^,)|(,$)/g, "");
                }
              } else {
                value = input.val();
              }
            }

          }

        }

        field = e.addField({
          label: confs[i].label,
          type: 'input',
          load: makeUpdateField,
          submit: makeSetField
        });

        input = $(field).find('input');
      }
    }
  }
}
