import json

from django import template
from django.template.defaulttags import register
from django.utils.safestring import mark_safe
from piffle.iiif import IIIFImageClient


@register.simple_tag(takes_context=True)
def querystring_replace(context, **kwargs):
    '''Template tag to simplify retaining querystring parameters
    when paging through search results with active filters.
    Example use:

        <a href="?{% querystring_replace page=paginator.next_page_number %}">
    '''
    # borrowed as-is from derrida codebase
    # inspired by https://stackoverflow.com/questions/2047622/how-to-paginate-django-with-other-get-variables

    # get a mutable copy of the current request
    querystring = context['request'].GET.copy()
    # update with any parameters passed in
    # NOTE: needs to *set* fields rather than using update,
    # because QueryDict update appends to field rather than replacing
    for key, val in kwargs.items():
        querystring[key] = val
    # return urlencoded query string
    return querystring.urlencode()



@register.simple_tag
def iiif_image(image_id, *args, **kwargs):
    '''Django template tag that provide IIIF image option logic via
    piffle. Example use:

        {% iiif_image my_image_uri width=200 %}

    '''
    if not image_id:
        return

    # piffle expects server and id separately; split them out
    img = IIIFImageClient(*image_id.rsplit('/', 1))

    # how much to generalize / what args to support here?
    if 'width' in kwargs:
        img = img.size(width=kwargs['width'])
    if 'height' in kwargs:
        img = img.size(height=kwargs['height'])

    return img

@register.filter(name='json')
def json_dumps(data):
    return mark_safe(json.dumps(data))
