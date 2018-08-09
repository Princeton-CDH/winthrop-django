import { mapActions } from 'vuex'

export default Vue.component('RangeFacet', {
    template: `
    <div class="range-facet">
        <div class="inputs">
            <sui-input :placeholder="minVal" @input="setMin"/>
            <label>to</label>
            <sui-input :placeholder="maxVal" />
        </div>
        <div class="histogram">
        </div>
    </div>
    `,
    props: {
        label: String,
        name: String,
        width: Number,
        choices: Array
    },
    computed: {
        minVal() {
            return this.choices
                .map(choice => parseInt(choice.value))
                .reduce((acc, cur) => cur < acc ? cur : acc, Infinity)
        },
        maxVal() {
            return this.choices
                .map(choice => parseInt(choice.value))
                .reduce((acc, cur) => cur > acc ? cur : acc, -Infinity)
        }
    },
    methods: {
        setMin(e) {
            console.log(this, e)
        },
    },
})