import { mapActions } from 'vuex'
import RangeFacet from './RangeFacet'

export default Vue.component('SearchFacet', {
    template: `
    <sui-grid-column :width="width" class="field">
        <label :for="label">{{ label }}</label>
        <template v-if="type === 'text'">
            <sui-input v-if="search" iconPosition="left" icon="search" placeholder="Search or select" v-model="filter" />
            <div v-if="search" class="rolodex">
                <button
                    v-for="letter in alphabet"
                    :key="letter"
                    class="letter"
                    :class="{active: alphaFilter == letter}"
                    @click.prevent="alphaFilter = alphaFilter == letter ? '' : letter"
                >
                {{ letter }}
                </button>
            </div>
            <div class="facets">
                <label v-if="availableChoices.length == 0">No results</label>
                <div
                    class="ui checkbox"
                    v-for="choice of choices"
                    v-show="availableChoices.includes(choice.value)"
                    :key="choice.value"
                >
                    <input
                        type="checkbox"
                        @input="toggleFacetChoice(choice)"
                        :name="choice.facet"
                        :value="choice.value"
                        :checked="choice.active"
                    />
                    <label>{{ choice.value }} <span class="count">{{ choice.count }}</span></label>
                </div>
            </div>
        </template>
        <range-facet v-if="type === 'range'" :label="label" :name="name" :width="width" :choices="choices">
        </range-facet>
    </sui-grid-column>
    `,
    components: {
        RangeFacet
    },
    data() {
        return {
            filter: '', // content of the search-within-facet box
            alphaFilter: '', // selected letter from the rolodex
            alphabet: String.fromCharCode(...Array(91).keys()).slice(65) // A-Z array used to generate the rolodex
        }
    },
    computed: {
        /**
         * Filters the list of facet choices based on the rolodex and 
         * search-within-facet box.
         * 
         * Returns an array of available choice *values* (not objects).
         * Choices are then hidden if their value isn't in the list.
         *
         * @returns {Array} available choice values
         */
        availableChoices() {
            return this.choices
                .map(choice => choice.value)
                .filter(value => this.normalize(value).startsWith(this.alphaFilter))
                .filter(value => this.match(value, this.filter))
        }
    },
    props: {
        type: String, // one of ['range', 'text']
        label: String, // user-friendly name, e.g. "Publication Date"
        name: String, // form-friendly name, e.g. "pub_date"
        search: Boolean, // whether to include the rolodex and search-within-facet box
        width: Number, // number of semantic UI grid columns; CDH grid has 12
        choices: Array // array of facet choice objects
    },
    methods: {
        ...mapActions([
            'toggleFacetChoice',
        ]),
        /**
         * Utility that normalizes strings for simple comparison.
         * Removes special characters, trims whitespace, and uppercases.
         *
         * @param {String} str input string
         * @returns {String} normalized string
         */
        normalize(str) {
            return str.replace(/[^\w\s]/gi, '').trim().toUpperCase()
        },
        /**
         * Compares two strings using normalize().
         * Return true if str2 matches str1.
         *
         * @param {String} str1 input string
         * @param {String} str2 compare string
         * @returns {Boolean} match
         */
        match(str1, str2) {
            return this.normalize(str1).includes(this.normalize(str2))
        },
    }
})