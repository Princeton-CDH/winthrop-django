import { mapState, mapActions } from 'vuex'

export default Vue.component('SearchSort', {
    template: `
    <div class="search-sort">
        <label>Sort By</label>
        <sui-dropdown
            :value="activeSort"
            :options="options"
            @input="sort($event)"
            selection
        />
    </div>
    `,
    computed: {
        ...mapState(['keywordQuery']),
        ...mapState('results', ['activeSort']),
        options() { // array of props for `sui-dropdown-item`s inside dropdown
            return [
                {
                    text: 'Author A-Z',
                    value: 'author_asc'
                },
                {
                    text: 'Author Z-A',
                    value: 'author_desc'
                },
                {
                    text: 'Year Oldest-Newest',
                    value: 'pub_year_asc'
                },
                {
                    text: 'Year Newest-Oldest',
                    value: 'pub_year_desc'
                },
                {
                    text: 'Relevance',
                    value: 'relevance',
                    disabled: this.keywordQuery ? false : true
                }
            ]
        },
    },
    methods: {
        ...mapActions('results', ['sort']),
    },
})
