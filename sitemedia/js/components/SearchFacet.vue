<script>
import { mapActions, mapState } from 'vuex'

export default {
    computed: {
        ...mapState([
            'facetChoices', // note these are from all facets together
        ]),
        /**
         * Filters all available facet choices to find the ones belonging
         * to this facet.
         *
         * @returns {Array} facet choices
         */
        choices() {
            return this.facetChoices.filter(choice => choice.facet === this.name)
        },
    },
    props: { // common to all facets
        label: String, // user-friendly name, e.g. "Publication Year"
        name: String, // form-friendly name, e.g. "pub_year"
        width: Number, // optional number of semantic UI grid columns to use; CDH grid has 12
    },
    methods: {
        ...mapActions([
            'toggleFacetChoice',
        ])
    },
}
</script>
