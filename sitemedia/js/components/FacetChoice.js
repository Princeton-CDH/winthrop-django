import { mapActions } from 'vuex'

export default Vue.component('FacetChoice', {
    template: `
    <div class="ui checkbox">
        <input
            type="checkbox"
            @input="toggleFacetChoice({ facet: name, value: value })"
            :name="name"
            :value="value"
            :checked="active"
        >
        <label>{{ value }} <span class="count">{{ count }}</span></label>
    </div>
    `,
    props: {
        name: String,
        value: String,
        count: Number,
        active: Boolean,
    },
    methods: {
        ...mapActions([
            'toggleFacetChoice'
        ])
    }
})