import isEmpty from 'lodash/isEmpty'
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
                <div class="active-facet-choice" v-for="(choice, index) in activeFacetChoices" :key="index">
                    <sui-label>
                        <span class="facet-name">{{ choice.facet }}: </span>
                        <span class="choice-name">{{ choice.value }}</span>
                        <sui-icon name="delete" @click="toggleFacetChoice(choice)" />
                    </sui-label>
                </div>
            </sui-segment>
            <sui-segment inverted>
                <slot name="sort"></slot>
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
        ]),
    },
    methods: {
        ...mapActions([
            'addFacets',
            'updateResults',
            'clearFacetChoices',
            'toggleFacetChoice',
            'setFormState',
            'updateURL',
        ]),
        ...mapMutations([
            'changeSort',
            'setFacetsEndpoint',
            'setResultsEndpoint',
        ]),
    },
    created() {
        this.setFacetsEndpoint(this.facetsEndpoint) // set endpoints
        this.setResultsEndpoint(this.resultsEndpoint)
        let initialState = {
            ...this.route.query,
            sort: this.route.query.sort || 'author_asc', // default if none selected
        }
        this.addFacets(initialState).then(() => this.setFormState(initialState)) // initialize form
    }
})
