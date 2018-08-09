import { mapState } from 'vuex'

export default Vue.component('SearchResults', {
    template: `<div class="search-results" v-html="results"></div>`,
    computed: {
        ...mapState([
            'results',
        ]),
    }
})