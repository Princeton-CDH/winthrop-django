/*
annotator translation integration

- adds an translation textarea field
- display translation name on marginalia item card when present
- stores translation on the annotation
*/

var translation = {
    // render extension to display translation on marginalia item card

    renderExtension: function(annotation, item) {
        // replace existing translation block with updated version
        var translation_div = translation.renderTranslation(annotation);
        item.find('.annotator-translation').remove();
        // insert translation (if any) before tags or footer, whichever comes first
        if (translation_div) {
            translation_div.insertBefore(item.find('.annotator-tags,.annotation-footer').first());
        }
        return item;
    },

    renderTranslation: function(annotation) {
        var translation_div;
        // display translation name with a label if present in the annotation
        if (annotation.translation) {
            translation_div = $('<div/>').addClass('annotator-translation').html(
                annotation.translation
          ).prepend($('<label>Annotation Translation:</label><br/>'));
        }
        return translation_div;
      },

     getEditorExtension: function getEditorExtension(options) {

      // editor extension to make translation editable
     return function editorExtension(e) {
        // The textarea element added to the Annotator.Editor wrapped in jQuery.
        // Cached to save having to recreate it everytime the editor is displayed.
        var field = null;
        var textarea = null;

        function updateField(field, annotation) {
            $(field).addClass('translation-lookup');
            // initialize textarea value & id when annotation.translation is present
            if (annotation.translation) {
                textarea.val(annotation.translation);

            } else {
                textarea.val('');
            }

            // configure autocomplete to look up translations from persons in the db

        }

        function setAnchorTranslation(field, annotation) {
            // store translation info on the annotation object
            if (textarea.val() != '') {
                annotation.translation = textarea.val();
            } else {
                // clear out translation if it was previously set
                annotation.translation = '';
            }
        }

        field = e.addField({
            label: 'Annotation Translation',
            type: 'textarea',
            load: updateField,
            submit: setAnchorTranslation

        });

        textarea = $(field).find('textarea');
    };
}

};
