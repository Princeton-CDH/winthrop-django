/*
annotator anchortext integration

- adds an anchortext textarea field
- display anchortext name on marginalia item card when present
- stores anchortext on the annotation
*/

var anchortext = {
    // render extension to display anchortext on marginalia item card

    renderExtension: function(annotation, item) {
        // replace existing anchortext block with updated version
        var anchortext_div = anchortext.renderAnchor(annotation);
        item.find('.annotator-anchortext').remove();
        // insert anchortext (if any) before tags or footer, whichever comes first
        if (anchortext_div) {
            anchortext_div.insertBefore(item.find('.annotator-tags,.annotation-footer').first());
        }
        return item;
    },

    renderAnchor: function(annotation) {
        var anchortext_div;
        // display anchortext name with a label if present in the annotation
        if (annotation.anchortext) {
            anchortext_div = $('<div/>').addClass('annotator-anchortext').html(
                annotation.anchortext
          ).prepend($('<label>Anchor Text:</label><br/>'));
        }
        return anchortext_div;
      },

     getEditorExtension: function getEditorExtension(options) {

      // editor extension to make anchortext editable
     return function editorExtension(e) {
        // The textarea element added to the Annotator.Editor wrapped in jQuery.
        // Cached to save having to recreate it everytime the editor is displayed.
        var field = null;
        var textarea = null;

        function updateField(field, annotation) {
            $(field).addClass('anchortext-lookup');
            // initialize textarea value & id when annotation.anchortext is present
            if (annotation.anchortext) {
                textarea.val(annotation.anchortext);
            } else {
                textarea.val('');
            }
        }

        function setAnchorText(field, annotation) {
            // store anchortext info on the annotation object
            if (textarea.val() != '') {
                annotation.anchortext = textarea.val();
            } else {
                // clear out anchortext if it was previously set
                annotation.anchortext = '';
            }
        }

        field = e.addField({
            label: 'Anchor Text',
            type: 'textarea',
            load: updateField,
            submit: setAnchorText
        });

        textarea = $(field).find('textarea');
    };
}

};
