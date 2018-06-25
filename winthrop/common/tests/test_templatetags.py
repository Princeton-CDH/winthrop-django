from unittest.mock import Mock

from django.http import QueryDict
from piffle.iiif import IIIFImageClient

from winthrop.common.templatetags.winthrop_tags import querystring_replace, \
    iiif_image


def test_querystring_replace():
    mockrequest = Mock()
    mockrequest.GET = QueryDict('query=saussure')
    context = {'request': mockrequest}
    # replace when arg is not present
    args = querystring_replace(context, page=1)
    # preserves existing args
    assert 'query=saussure' in args
    # adds new arg
    assert 'page=1' in args

    mockrequest.GET = QueryDict('query=saussure&page=2')
    args = querystring_replace(context, page=3)
    assert 'query=saussure' in args
    # replaces existing arg
    assert 'page=3' in args
    assert 'page=2' not in args

    # handle repeating terms
    mockrequest.GET = QueryDict('language=english&language=french')
    args = querystring_replace(context, page=10)
    assert 'language=english' in args
    assert 'language=french' in args
    assert 'page=10' in args


def test_iiif_image():

    test_img_server = 'http://example.com/imgserver'
    test_img_id = 'foo-bar-baz.jp2'
    test_img_uri = '/'.join([test_img_server, test_img_id])

    iiif_img = IIIFImageClient(test_img_server, test_img_id)

    assert str(iiif_image(test_img_uri)) == str(iiif_img)
    assert str(iiif_image(test_img_uri, width=200)) == str(iiif_img.size(width=200))
    assert str(iiif_image(test_img_uri, height=100)) == str(iiif_img.size(height=100))
    assert str(iiif_image(test_img_uri, width=200, height=100)) == \
        str(iiif_img.size(width=200, height=100))

    assert iiif_image('') == None
