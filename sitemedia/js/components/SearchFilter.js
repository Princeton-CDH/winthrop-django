import FilterChoice from './FilterChoice'

export default Vue.component('SearchFilter', {
    template: `
    <sui-segment>
        <label :for="label">{{ label }}</label>
            <filter-choice
                v-for="choice in choices"
                @input="$emit('input')"
                :key="choice.label"
                :name="label"
                :label="choice"
                :value="choice"
            />
        <label>books</label>
    </sui-segment>
    `,
    components: {
        FilterChoice
    },
    props: {
        label: String,
        choices: Array
    },
    data() {
        return {
            activeFilters: []
        }
    }
})