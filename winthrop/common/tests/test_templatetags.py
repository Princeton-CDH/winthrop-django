from unittest.mock import Mock

from django.http import QueryDict

from winthrop.common.templatetags.winthrop_tags import querystring_replace


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
