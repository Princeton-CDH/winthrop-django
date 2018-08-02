import { mapState } from 'vuex'

export default Vue.component('SearchResults', {
    template: `<div class="search-results" v-html="results" />`,
    computed: {
        ...mapState([
            'results',
            'totalResults',
        ]),
    }
})