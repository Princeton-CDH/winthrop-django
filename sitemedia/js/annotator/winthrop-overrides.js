/*
Winthrop Annotator Overrides and Extensions
-A simple jQuery shim to fix the text on the 'Comment' box to something more
sensible

-Extensions that add needed fields for the Winthrop family on the page project:
    -annotation translation
    -annotation language
    -anchor text
    -anchor text translation

*/

var fixComment = function(field) {
  // field - any valid jQuery selector for the annotation text field
  $(field).attr('placeholder', 'Annotation text...')
}

var translation = {
  getEditorExtension: function getEditorExtension() {

    // editor extension to make author editable
    return function editorExtension(e) {
      // The input element added to the Annotator.Editor wrapped in jQuery.
      // Cached to save having to recreate it everytime the editor is displayed.
      var field = null;
      var input = null;

      function updateField(field, annotation) {
        if (annotation.translation) {
          input.val(annotation.translation);
        } else {
          input.val('');
        }
      }

      function setTranslation(field, annotation) {
        if (input.val() != '') {
          annotation.translation = input.val()
        }
      }

      field = e.addField({
        label: 'Enter annotation translation',
        type: 'textarea',
        load: updateField,
        submit: setTranslation
      });

      input = $(field).find('input');
    };

  }
}

var anchorText = {
  getEditorExtension: function getEditorExtension() {

    // editor extension to make author editable
    return function editorExtension(e) {
      // The input element added to the Annotator.Editor wrapped in jQuery.
      // Cached to save having to recreate it everytime the editor is displayed.
      var field = null;
      var input = null;

      function updateField(field, annotation) {
        if (annotation.anchortext) {
          input.val(annotation.anchortext);
        } else {
          input.val('');
        }
      }

      function setAnchorText(field, annotation) {
        if (input.val() != '') {
          annotation.anchortext = input.val()
        }
      }

      field = e.addField({
        label: 'Enter anchor text',
        type: 'textarea',
        load: updateField,
        submit: setAnchorText
      });

      input = $(field).find('input');
    };

  }
}
