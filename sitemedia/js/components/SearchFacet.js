import SearchFacetChoice from './SearchFacetChoice'

export default Vue.component('SearchFacet', {
    template: `
    <sui-grid-column :width="width" class="field">
        <label :for="label">{{ label }}</label>
        <template v-if="type === 'text'">
            <div v-if="search" class="search" />
            <div v-if="search" class="rolodex" />
            <div v-if="choices" class="facets">
                <search-facet-choice
                    v-for="choice in choices"
                    :facet="label"
                    :label="choice.label"
                    :count="choice.count"
                />
            </div>
            <div>{{ values }}</div>
        </template>
        <template v-if="type === 'range'">
            <h1>range facet</h1>
        </template>
    </sui-grid-column>
    `,
    data() {
        return {
            values: this.choices
        }
    },
    components: {
        SearchFacetChoice
    },
    props: {
        type: String,
        label: String,
        search: {
            type: Boolean,
            default: false
        },
        width: Number,
        choices: Array
    },
})