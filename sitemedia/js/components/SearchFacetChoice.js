export default Vue.component('SearchFacetChoice', {
    template: `
    <div class="ui checkbox">
        <input
            type="checkbox"
            :name="label"
            :checked="checked"
            v-model="checked"
            @change="$emit('toggle-facet', label)"
        >
        <label>{{ label }} <span class="count">{{ count }}</span></label>
    </div>
    `,
    props: {
        checked: Boolean,
        label: String,
        count: Number
    }
})