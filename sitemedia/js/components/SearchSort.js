import { mapState, mapActions } from 'vuex'

export default Vue.component('SearchSort', {
    template: `
    <div class="search-sort">
        <label>Sort By</label>
        <sui-dropdown
            :value="activeSort"
            :options="options"
            @input="changeSort($event)"
            selection
        />
    </div>
    `,
    computed: {
        ...mapState([
            'activeSort',
            'query'
        ]),
        options() {
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
                    disabled: this.query ? false : true
                }
            ]
        },
    },
    methods: {
        ...mapActions([
            'changeSort'
        ]),
    },
})
