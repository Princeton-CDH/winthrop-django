/*
annotator anchorTranslation integration

- adds an anchorTranslation textarea field
- display anchorTranslation name on marginalia item card when present
- stores anchorTranslation on the annotation
*/

var anchorTranslation = {
    // render extension to display anchorTranslation on marginalia item card

    renderExtension: function(annotation, item) {
        // replace existing anchorTranslation block with updated version
        var anchorTranslation_div = anchorTranslation.renderAnchorTranslation(annotation);
        item.find('.annotator-anchorTranslation').remove();
        // insert anchorTranslation (if any) before tags or footer, whichever comes first
        if (anchorTranslation_div) {
            anchorTranslation_div.insertBefore(item.find('.annotator-tags,.annotation-footer').first());
        }
        return item;
    },

    renderAnchorTranslation: function(annotation) {
        var anchorTranslation_div;
        // display anchorTranslation name with a label if present in the annotation
        if (annotation.anchorTranslation) {
            anchorTranslation_div = $('<div/>').addClass('annotator-anchorTranslation').html(
                annotation.anchorTranslation
          ).prepend($('<label>Anchor text translation:</label><br/>'));
        }
        return anchorTranslation_div;
      },

     getEditorExtension: function getEditorExtension(options) {

      // editor extension to make anchorTranslation editable
     return function editorExtension(e) {
        // The textarea element added to the Annotator.Editor wrapped in jQuery.
        // Cached to save having to recreate it everytime the editor is displayed.
        var field = null;
        var textarea = null;

        function updateField(field, annotation) {
            $(field).addClass('anchorTranslation');
            // initialize textarea value & id when annotation.anchorTranslation is present
            if (annotation.anchorTranslation) {
                textarea.val(annotation.anchorTranslation);

            } else {
                textarea.val('');
            }

            // configure autocomplete to look up anchorTranslations from persons in the db

        }

        function setAnchorTranslation(field, annotation) {
            // store anchorTranslation info on the annotation object
            if (textarea.val() != '') {
                annotation.anchorTranslation = textarea.val();
            } else {
                // clear out anchorTranslation if it was previously set
                annotation.anchorTranslation = '';
            }
        }

        field = e.addField({
            label: 'Anchor Translation',
            type: 'textarea',
            load: updateField,
            submit: setAnchorTranslation
        });

        textarea = $(field).find('textarea');
    };
}

};
