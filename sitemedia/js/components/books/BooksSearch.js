import { mapGetters, mapActions, mapState, mapMutations } from 'vuex'
import { isEmpty } from 'lodash'

import SearchFacet from '../SearchFacet'
import SearchSort from '../SearchSort'

export default Vue.component('BooksSearch', {
    template: `
    <div class="books-search">
        <sui-container textAlign="center" text>
            <h4 is="sui-header" class="results-count">
            Displaying {{ totalResults }} {{ totalResults | pluralize('book') }}
            </h4>
        </sui-container>
        <form class="search-form ui form">
            <sui-menu tabular attached="top">
                <div
                    is="sui-menu-item"
                    v-for="(tab, index) in tabs"
                    :key="index"
                    :active="activeTab === index"
                    :content="tabLabel(tab)"
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
                        v-for="facetName in tab"
                        v-bind="facetConfig.find(facet => facet.name === facetName)"
                        :choices="facetChoices.filter(choice => choice.facet === facetName)"
                        :key="facetName"
                    >
                    </search-facet>
                </div>
            </sui-segment>
            <sui-segment inverted class="active-items">
                <label>Selected</label>
                <div class="active-facet-choice" v-for="(choice, index) in activeFacetChoices" :key="index">
                    <sui-label>
                        <span class="facet-name">{{ facetConfig.find(facet => facet.name === choice.facet).label }}: </span>
                        <span class="choice-name">{{ choice.value }}</span>
                        <sui-icon name="delete" @click="toggleFacetChoice(choice)" />
                    </sui-label>
                </div>
            </sui-segment>
            <sui-segment inverted>
                <search-sort></search-sort>
            </sui-segment>
        </form>
    </div>`,
    components: {
        SearchFacet,
        SearchSort,
    },
    data() {
        return {
            tabs: [ // array of arrays specifying how facets should be grouped into tabs
                ['author', 'editor'],
                ['pub_year'],
                ['language', 'subject'],
                ['annotator']
            ],
            activeTab: 0, // index of currently active tab
            facetConfig: [ // array of props for `SearchFacet`s
                {
                    name: 'author',
                    label: 'Author',
                    type: 'text',
                    search: true,
                    width: 6,
                },
                {
                    name: 'editor',
                    label: 'Editor',
                    type: 'text',
                },
                {
                    name: 'pub_year',
                    label: 'Publication Year',
                    type: 'range',
                },
                {
                    name: 'language',
                    label: 'Language',
                    type: 'text',
                },
                {
                    name: 'subject',
                    label: 'Subject',
                    type: 'text',
                },
                {
                    name: 'annotator',
                    label: 'Annotator',
                    type: 'text',
                },
            ],
        }
    },
    computed: {
        ...mapState([
            'totalResults',
            'facetChoices',
        ]),
        ...mapGetters([
            'activeFacets',
            'activeFacetChoices',
            'formState',
        ]),
    },
    created() {
        this.setEndpoint('facets/') // facet data URL will become the current url (/books) + '/facets'
        if (isEmpty(this.formState)) { // if nothing was active on the form (i.e. fresh page load)
            this.changeSort('author_asc') // default to author a-z sort
            this.updateURL() // add the sort to the URL so it's used when fetching results & facets
        }
        this.loadSearchData() // load initial facet data and results
    },
    methods: {
        ...mapActions([
            'loadResults',
            'loadSearchData',
            'clearFacetChoices',
            'toggleFacetChoice',
            'setEndpoint',
            'updateURL'
        ]),
        ...mapMutations([
            'changeSort'
        ]),
        /**
         * Generate a string label for search widget tabs.
         * Joins the matching label for each facet name in the tab with a separator.
         *
         * @param {Array} tab array of string names of the facets in the tab, from data.tabs
         * @returns {String} label for the tab
         */
        tabLabel(tab, separator = '  ·  ') {
            return tab
                .map(facetName => this.facetConfig.find(facet => facet.name === facetName).label)
                .join(separator)
        },
    },
})
