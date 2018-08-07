import { mapState } from 'vuex'

export default Vue.component('SearchResults', {
    template: `
    <div class="search-results">
        <slot v-html="results" />
    </div>`,
    computed: {
        ...mapState([
            'results',
            'totalResults',
        ]),
    }
})