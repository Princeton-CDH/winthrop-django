export default Vue.component('FacetChoice', {
    template: `
    <div class="ui checkbox">
        <input type="checkbox" :value="value" @input="$emit('input', $event.target.value)" :name="name">
        <label>{{ label }} <span class="count">{{ count }}</span></label>
    </div>
    `,
    props: {
        name: String,
        value: String,
        label: String,
        count: Number
    }
})