/*
Winthrop Annotator Plugin
- Requiresments: jQuery, annotator.js 2.0+, marginalia
- add object 'winthrop' with methods to create a renderextension
and editor extension for Winthrop Family on the Page Project
- conf objects should specify the following properties: name, label, and type (if list)
  and eventualy autocompletes
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
      if (fieldValue || fieldValue == 0) {
        // split arrays into a comma delimited string
        if ($.isArray(fieldValue)) {
          div = $('<div/>').addClass('annotator-'+conf.name).html(function () {
          return '<label>'+conf.label+'</label>' + $.map(fieldValue, function (value) {
            }).join(', ');
          });
        }
      else {
        // otherwise return the field value
        div = $('<div/>').addClass('annotator-'+conf.name).html(
            fieldValue
          ).prepend($('<label>'+conf.label+':</label>'));
      }
    }
      return div;
    }
    // rendered function that iterates over confs array
    return function(annotation, item) {
      for (i in confs) {
        // Invoke renderField with options as passed to function
        var div = renderField(annotation[confs[i].name], confs[i]);
        item.find('.annotator-' + confs[i].name).remove();
        if (div != null) {
          div.insertAfter(item.find('.text' + (i != 0 ? ',.' + confs[i - 1].name : '')).last())
        }
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
              annotation[conf.name] = values[i].trim().replace(/(^,)|(,$)/g, "");
            }
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
          if (annotation.type == 'list') {
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
        field = e.addField({
          label: confs[i].label,
          type: 'input'
        });

        input = $(field).find('input');
        fields = e.fields
        // Add the load and submit functions now that
        // we have an input DOM object
        for (var j in fields) {
          if (fields[j].label == confs[i].label) {
            fields[j].load = makeUpdateField(confs[i], input);
            fields[j].submit = makeSetField(confs[i], input);
          }
        }
      }
    }
  }
}
