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
            filter: '',
            alphaFilter: '',
            alphabet: String.fromCharCode(...Array(91).keys()).slice(65)
        }
    },
    computed: {
        availableChoices() {
            return this.choices
                .map(choice => choice.value)
                .filter(value => this.normalize(value).startsWith(this.alphaFilter))
                .filter(value => this.match(value, this.filter))
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
        ...mapActions([
            'toggleFacetChoice',
        ]),
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