export default {
    tabs: [
        ['Author', 'Editor', 'Translator'],
        ['Publisher', 'Publication Year'],
        ['Language', 'Subject'],
        ['Annotator']
    ],
    active: 0,
    filters: [
        {
            label: 'Only display',
            choices: [
                'Annotated',
                'Digitized'
            ]
        }
    ],
    facets: [
        {
            label: 'Author',
            name: 'author_exact',
            type: 'text',
            search: true,
            width: 6,
            choices: [
                {'label': 'Copus, Martinus', 'count': 1},
                {'label': 'Rous, Francis, 1615-', 'count': 6},
                {'label': 'Biancani, Giuseppe', 'count': 12},
                {'label': 'Herdson, Henry', 'count': 1},
                {'label': 'Moolen, Simon va: de', 'count': 2},
                {'label': 'Clüver, Philipp: 1580-1622', 'count': 3},
                {'label': 'Sira, Ben', 'count': 1},
            ],
        },
        {
            label: 'Editor',
            name: 'editor_exact',
            type: 'text',
            choices: []
        },
        {
            label: 'Translator',
            name: 'translator_exact',
            type: 'text',
            choices: []
        },
        {
            label: 'Publisher',
            name: 'publisher_exact',
            type: 'text',
            choices: []
        },
        {
            label: 'Publication Year',
            name: 'pub_year',
            type: 'range'
        },
        {
            label: 'Language'
        },
        {
            label: 'Subject',
        },
        {
            label: 'Annotator'
        }
    ],
    formState: []
}