import { mapGetters, mapActions, mapState } from 'vuex'

import SearchFacet from '../SearchFacet'
import SearchFilter from '../SearchFilter'

export default Vue.component('BooksSearch', {
    template: `
    <div class="books-search">
        <sui-container textAlign="center" text>
            <h4 is="sui-header" class="results-count">Displaying {{ totalResults }} {{ totalResults | pluralize('book') }}</h4>
        </sui-container>
        <form class="search-form ui form">
            <sui-menu tabular attached="top">
                <div
                    is="sui-menu-item"
                    v-for="(tab, index) in tabs"
                    :key="index"
                    :active="activeTab === index"
                    :content="tab.map(facet => facetConfig[facet].label).join(' · ')"
                    @click="activeTab = index"
                />
            </sui-menu>
            <sui-segment
                v-for="(tab, index) in tabs"
                :key="index"
                :class="{ active: activeTab === index }"
                class="bottom attached tab"
            >
                <div class="ui equal width stackable grid">
                    <search-facet
                        v-for="facet in tab"
                        v-bind="facetConfig[facet]"
                        :name="facet"
                        :choices="facets[facet]"
                        :key="facet"
                    >
                    </search-facet>
                </div>
            </sui-segment>
            <sui-segment inverted>
                <label>Selected</label>
                <div v-for="(choices, facet) in activeFacets" :key="facet">
                    <label>{{ facetConfig[facet].label }}:</label>
                    <sui-label v-for="choice in choices" :key="choice.value">
                        {{ choice.value }}
                        <sui-icon name="delete" />
                    </sui-label>
                </div>
                <a v-if="Object.keys(activeFacets).length > 0">Clear All</a>
            </sui-segment>
        </form>
    </div>`,
    components: {
        SearchFacet,
        SearchFilter
    },
    data() {
        return {
            tabs: [
                ['author', 'editor', 'translator'],
                ['publisher', 'pub_year'],
                ['language', 'subject'],
                ['annotator']
            ],
            activeTab: 0,
            facetConfig: {
                author: {
                    label: 'Author',
                    type: 'text',
                    search: true,
                    width: 6,
                },
                editor: {
                    label: 'Editor',
                    type: 'text',
                },
                translator: {
                    label: 'Translator',
                    type: 'text',
                },
                publisher: {
                    label: 'Publisher',
                    type: 'text',
                },
                pub_year: {
                    label: 'Publication Year',
                    type: 'range',
                },
                language: {
                    label: 'Language',
                    type: 'text',
                },
                subject: {
                    label: 'Subject',
                    type: 'text',
                },
                annotator: {
                    label: 'Annotator',
                    type: 'text',
                },
            },
        }
    },
    computed: {
        ...mapState([
            'facets',
            'filters',
            'totalResults',
        ]),
        ...mapGetters([
            'activeFacets',
        ]),
    },
    created() {
        this.loadFacetData('/static/js/components/books/data.json')
    },
    methods: {
        ...mapActions([
            'loadFacetData',
            'clearFacetChoices',
        ]),
    },
})
