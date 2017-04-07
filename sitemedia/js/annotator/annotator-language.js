/*
annotator language integration

- adds an language input field
- display language name on marginalia item card when present
- stores language on the annotation
*/

var language = {
    // render extension to display language on marginalia item card

    renderExtension: function(annotation, item) {
        // replace existing language block with updated version
        var language_div = language.renderLanguage(annotation);
        item.find('.annotator-language').remove();
        // insert language (if any) before tags or footer, whichever comes first
        if (language_div) {
            language_div.insertBefore(item.find('.annotator-tags,.annotation-footer').first());
        }
        return item;
    },

    renderLanguage: function(annotation) {
        var language_div;
        // display language name with a label if present in the annotation
        // modeled on marginalia tag renderer
        if (annotation.language && .isArray(annotation.language)) {
            languages =  $('<div/>').addClass('annotator-language').html(
                annotation.language
          ).prepend($('<label>Annotation Translation:</label>'));
        }
        return language_div;
      },

     getEditorExtension: function getEditorExtension(options) {

      // editor extension to make language editable
     return function editorExtension(e) {
        // The input element added to the Annotator.Editor wrapped in jQuery.
        // Cached to save having to recreate it everytime the editor is displayed.
        var field = null;
        var input = null;

          // Function to parse a list of tags and only autocomplete on what's after the
          // comma.
          var parseRecentTag = function(str) {
            var list = str.split(',');
            var latest = list[list.length - 1]
            return latest.trim()
          }

        function updateField(field, annotation) {
            $(field).addClass('language-lookup');
            // initialize input value & id when annotation.language is present
            if (annotation.language){
              languages = annotation.language.join(', ')
              input.val(languages)
            } else {
                input.val('');
            }

            // configure autocomplete to look up languages from persons in the db

        }

        function setLanguage(field, annotation) {
            // store language info on the annotation object
            if (input.val() != '') {
              var languages = input.val().split(',')
              for (i = 0; i < languages.length(), i++) {
                languages[i] = language[i].strip()
                annotation.language = languages
              }
            } else {
                // clear out language if it was previously set
                annotation.language = [];
            }
        }

        field = e.addField({
            label: 'Annotation Translation',
            type: 'input',
            load: updateField,
            submit: setLanguage
        });

        input = $(field).find('input');
    };
}

};
