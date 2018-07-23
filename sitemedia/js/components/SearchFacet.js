import FacetChoice from './FacetChoice'

export default Vue.component('SearchFacet', {
    template: `
    <sui-grid-column :width="width" class="field">
        <label :for="label">{{ label }}</label>
        <template v-if="type === 'text'">
            <div v-if="search" class="search" />
            <div v-if="search" class="rolodex" />
            <div v-if="choices" class="facets">
                <facet-choice
                    v-for="choice in choices"
                    @input="$emit('input')"
                    :key="choice.label"
                    :name="label"
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
    props: {
        type: String,
        label: String,
        search: {
            type: Boolean,
            default: false
        },
        width: Number,
        choices: Array
    }
})