import { mapActions } from 'vuex'

export default Vue.component('FacetChoice', {
    template: `
    <div class="ui checkbox">
        <input
            type="checkbox"
            @input="toggleFacetChoice({ facet: facet, value: value, active: active, count: count })"
            :name="facet"
            :value="value"
            :checked="active"
        >
        <label>{{ value }} <span class="count">{{ count }}</span></label>
    </div>`,
    props: {
        facet: String,
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