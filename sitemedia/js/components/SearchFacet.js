import FacetChoice from './FacetChoice'

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
            <div v-if="choices" class="facets">
                <facet-choice
                    v-for="choice in choices"
                    v-show="availableChoices.includes(choice.label)"
                    @input="$emit('input')"
                    :key="choice.label"
                    :name="name"
                    :label="choice.label"
                    :count="choice.count"
                    :value="choice.label"
                />
            </div>
        </template>
        <template v-if="type === 'range'">
            <h1>range facet</h1>
        </template>
    </sui-grid-column>
    `,
    components: {
        FacetChoice
    },
    data() {
        return {
            filter: '',
            alphaFilter: '',
            alphabet: String.fromCharCode(...Array(91).keys()).slice(65)
        }
    },
    computed: {
        availableChoices() {
            return this.choices
                .map(choice => choice.label)
                .filter(label => this.normalize(label).startsWith(this.alphaFilter))
                .filter(label => this.match(label, this.filter))
        }
    },
    props: {
        type: String,
        label: String,
        name: String,
        search: {
            type: Boolean,
            default: false
        },
        width: Number,
        choices: Array
    },
    methods: {
        /**
         * Utility that normalizes strings for simple comparison.
         * Removes special characters, trims whitespace, and uppercases.
         *
         * @param {String} str
         * @returns {String}
         */
        normalize(str) {
            return str.replace(/[^\w\s]/gi, '').trim().toUpperCase()
        },
        /**
         * Compares two strings using normalize().
         * Return true if str2 matches str1.
         *
         * @param {String} str1
         * @param {String} str2
         * @returns {Boolean}
         */
        match(str1, str2) {
            return this.normalize(str1).includes(this.normalize(str2))
        },
    }
})