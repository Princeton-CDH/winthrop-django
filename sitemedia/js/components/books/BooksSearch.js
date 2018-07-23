import SearchFacet from '../SearchFacet'

export default Vue.component('BooksSearch', {
    template: `<form class="search-form ui form">
        <sui-menu tabular attached="top">
            <div
                is="sui-menu-item"
                v-for="(tab, index) in tabs"
                :key="index"
                :active="isActive(index)"
                :content="tab.join(' · ')"
                @click="select(index)"
            />
        </sui-menu>
        <sui-segment
            v-for="(tab, index) in tabs"
            :key="index"
            :class="{ active: isActive(index) }"
            class="bottom attached tab"
        >
            <div class="ui equal width stackable grid">
                <search-facet
                    v-for="facet in tab"
                    @input="submit"
                    :key="facet"
                    :label="facet"
                    :type="facets[facet].type"
                    :search="facets[facet].search"
                    :choices="facets[facet].choices"
                    :width="facets[facet].width"
                />
            </div>
        </sui-segment>
    </form>`,
    components: {
        SearchFacet
    },
    data() {
        return {
            tabs: [
                ['Author', 'Editor', 'Translator'],
                ['Publisher', 'Publication Year'],
                ['Language', 'Subject'],
                ['Annotator']
            ],
            active: 0,
            facets: {
                'Author': {
                    'type': 'text',
                    'search': true,
                    'width': 6,
                    'choices': [
                        {'label': 'Copus, Martinus', 'count': 1},
                        {'label': 'Rous, Francis, 1615-', 'count': 6},
                        {'label': 'Biancani, Giuseppe', 'count': 12},
                        {'label': 'Herdson, Henry', 'count': 1},
                        {'label': 'Moolen, Simon va: de', 'count': 2},
                        {'label': 'Clüver, Philipp: 1580-1622', 'count': 3},
                        {'label': 'Sira, Ben', 'count': 1},
                    ],
                },
                'Editor': {
                    'type': 'text',
                    'choices': [
                        {'label': 'Copus, Martinus', 'count': 1},
                        {'label': 'Rous, Francis, 1615-', 'count': 6},
                        {'label': 'Biancani, Giuseppe', 'count': 12},
                        {'label': 'Herdson, Henry', 'count': 1},
                        {'label': 'Moolen, Simon va: de', 'count': 2},
                        {'label': 'Clüver, Philipp: 1580-1622', 'count': 3},
                        {'label': 'Sira, Ben', 'count': 1},
                    ],
                },
                'Translator': {
                    'type': 'text',
                    'choices': [
                        {'label': 'Copus, Martinus', 'count': 1},
                        {'label': 'Rous, Francis, 1615-', 'count': 6},
                        {'label': 'Biancani, Giuseppe', 'count': 12},
                        {'label': 'Herdson, Henry', 'count': 1},
                        {'label': 'Moolen, Simon va: de', 'count': 2},
                        {'label': 'Clüver, Philipp: 1580-1622', 'count': 3},
                        {'label': 'Sira, Ben', 'count': 1},
                    ],
                },
                'Publisher': {
                    'type': 'text',
                    'search': true,
                    'width': 8,
                    'choices': [
                        {'label': 'Copus, Martinus', 'count': 1},
                        {'label': 'Rous, Francis, 1615-', 'count': 6},
                        {'label': 'Biancani, Giuseppe', 'count': 12},
                        {'label': 'Herdson, Henry', 'count': 1},
                        {'label': 'Moolen, Simon va: de', 'count': 2},
                        {'label': 'Clüver, Philipp: 1580-1622', 'count': 3},
                        {'label': 'Sira, Ben', 'count': 1},
                    ],
                },
                'Publication Year': {
                    'type': 'range',
                    'choices': [
                        {'label': '1765', 'count': 5},
                        {'label': '1766', 'count': 2},
                        {'label': '1768', 'count': 1},
                        {'label': '1785', 'count': 1},
                        {'label': '1795', 'count': 1},
                        {'label': '1843', 'count': 9},
                    ]
                },
                'Language': {},
                'Subject': {},
                'Annotator': {},
            }
        }
    },
    methods: {
        isActive(tabIndex) {
          return this.active === tabIndex
        },
        select(tabIndex) {
          this.active = tabIndex
        },
        submit() {
            let data = $(this.$el).serializeArray()
            console.log(data)
        }
    },
})