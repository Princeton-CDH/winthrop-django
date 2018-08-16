import { mapGetters, mapActions, mapState, mapMutations } from 'vuex'

export default Vue.component('SearchForm', {
    template: `
    <div class="books-search">
        <sui-container textAlign="center" text>
            <h4 is="sui-header" class="results-count">
            Displaying {{ totalResults }} {{ totalResults | pluralize(resource) }}
            </h4>
        </sui-container>
        <form class="search-form ui form">
            <slot name="tabs"></slot>
            <sui-segment inverted class="active-items">
                <label>Selected</label>
                <div class="active-facet-choice" v-for="facet in activeRangeFacets" :key="facet.name">
                    <sui-label>
                        <span class="facet-name">{{ facet.name }}: </span>
                        <span class="choice-name">
                            <span v-if="rangeFacetMinMax(facet.name).minVal">
                                {{ rangeFacetMinMax(facet.name).minVal }}
                            </span>
                            <span> - </span>
                            <span v-if="rangeFacetMinMax(facet.name).maxVal">
                                {{ rangeFacetMinMax(facet.name).maxVal }}
                            </span>
                        </span>
                        <sui-icon name="delete" @click="clearRangeFacet(facet.name)" />
                    </sui-label>
                </div>
                <div class="active-facet-choice" v-for="(choice, index) in activeFacetChoices" :key="index">
                    <sui-label>
                        <span class="facet-name">{{ choice.facet }}: </span>
                        <span class="choice-name">{{ choice.value }}</span>
                        <sui-icon name="delete" @click="toggleFacetChoice(choice)" />
                    </sui-label>
                </div>
                <label
                    class="clear-all"
                    v-if="activeFacetChoices.length > 0 || activeRangeFacets.length > 0"
                    @click="clearFacets">
                    Clear All</label>
            </sui-segment>
            <sui-segment inverted class="result-controls">
                <slot name="sort"></slot>
                <slot name="pagination"></slot>
            </sui-segment>
        </form>
    </div>`,
    props: {
        resource: String,
        resultsEndpoint: String,
        facetsEndpoint: String,
    },
    computed: {
        ...mapState([
            'route',
            'totalResults',
        ]),
        ...mapGetters([
            'activeFacetChoices',
            'activeRangeFacets',
            'rangeFacetMinMax',
        ]),
    },
    methods: {
        ...mapActions([
            'addFacets',
            'updateResults',
            'clearFacets',
            'toggleFacetChoice',
            'clearRangeFacet',
            'setFormState',
            'updateURL',
        ]),
        ...mapMutations([
            'results/sort',
            'results/setEndpoint',
            'setFacetsEndpoint',
        ]),
    },
    created() {
        this.setFacetsEndpoint(this.facetsEndpoint) // set endpoints
        this['results/setEndpoint'](this.resultsEndpoint)
        let initialState = {
            ...this.route.query,
            sort: this.route.query.sort || 'author_asc', // default if none selected
            page: this.route.query.page || 1 // default if none selected
        }
        this.addFacets(initialState).then(() => this.setFormState(initialState)) // initialize form
    }
})
