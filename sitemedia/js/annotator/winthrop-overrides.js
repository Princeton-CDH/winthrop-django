/*
Winthrop Annotator Override
-A simple jQuery shim to fix the text on the 'Comment' box to something more
sensible

*/

var fixComment = function(field) {
  // field - any valid jQuery selector for the annotation text field
  $(field).attr('placeholder', 'Annotation text...')
}
