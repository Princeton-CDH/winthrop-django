import SearchFacet from './SearchFacet'

export default Vue.component('TextFacet', {
    extends: SearchFacet, // inherit default facet settings
    template: `
    <sui-grid-column :width="width" class="field">
        <label :for="label">{{ label }}</label>
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
                v-for="(choice, index) of choices"
                v-show="availableChoices.includes(choice.value)"
                :key="choice.value"
            >
                <input
                    :id="inputID(name, index)"
                    type="checkbox"
                    @input="toggleFacetChoice(choice)"
                    :name="name"
                    :value="choice.value"
                    :checked="choice.active"
                />
                <label :for="inputID(name, index)">
                    {{ choice.value }} <span class="count">{{ choice.count }}</span>
                </label>
            </div>
        </div>
    </sui-grid-column>
    `,
    props: {
        search: Boolean, // whether to include the rolodex and search-within-facet box
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
    methods: {
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
        inputID(name, index) {
            return `${name}-choice-${index}`
        },
    },
})