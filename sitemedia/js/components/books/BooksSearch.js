import { mapGetters, mapActions, mapState, mapMutations } from 'vuex'
import isEqual from 'lodash/isEmpty'

import SearchFacet from '../SearchFacet'
import SearchFilter from '../SearchFilter'
import SearchSort from '../SearchSort'
import { isEmpty } from '../../../../node_modules/rxjs/operators';

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
        SearchFilter,
        SearchSort,
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
            facetConfig: [
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
                    name: 'translator',
                    label: 'Translator',
                    type: 'text',
                },
                {
                    name: 'publisher',
                    label: 'Publisher',
                    type: 'text',
                    search: true,
                    width: 6
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
            'filters',
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
        this.setEndpoint('facets/')
        if (isEmpty(this.formState)) { // if nothing was selected
            this.changeSort('author_asc') // default to author a-z sort
            this.updateURL()
        }
        this.loadSearchData()
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
         * @param {Array} tab
         * @returns {String}
         */
        tabLabel(tab, separator = '  ·  ') {
            return tab
                .map(facetName => this.facetConfig.find(facet => facet.name === facetName).label)
                .join(separator)
        },
    },
})
