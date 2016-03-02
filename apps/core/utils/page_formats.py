# -*- coding: utf-8 -*-

PAGE_FORMATS_INFO = (
    (
        'a4-port',
        {
            'title': u'A4 портретный',
            'width': 210,
            'height': 297,
        },
    ),
    (
        'a4-album',
        {
            'title': u'A4 альбомный',
            'width': 297,
            'height': 210,
        },
    ),
    (
        'a5-port',
        {
            'title': u'A5 портретный',
            'width': 148,
            'height': 210,
        },
    ),
    (
        'a5-album',
        {
            'title': u'A5 альбомный',
            'width': 210,
            'height': 148,
        },
    ),
)

PAGE_FORMATS_INFO_CHOICES = [(x[0], x[1]['title']) for x in PAGE_FORMATS_INFO]