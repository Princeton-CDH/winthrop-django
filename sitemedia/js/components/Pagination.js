import { mapState, mapGetters } from 'vuex'

export default Vue.component('Pagination', {
    template: `
    <div class="pagination">
        <div class="page-controls">
            <a rel="prev" is="sui-button" icon="chevron left" @click="previous" :disabled="current < 2"></a>
            <a is="sui-button" @click="go(1)" v-if="current > 3">1</a>
            <sui-icon name="ellipsis horizontal" v-if="current > 4 && total > 6"/>
            <a is="sui-button" v-for="page in displayRange" @click="go(page)" :active="current === page">{{ page }}</a>
            <sui-icon name="ellipsis horizontal" v-if="current < total - 3 && total > 6"/>
            <a is="sui-button" @click="go(total)" v-if="current < total - 2">{{ total }}</a>
            <a rel="next" is="sui-button" icon="chevron right" @click="next" :disabled="current > total - 1"></a>
        </div>
    </div>
    `,
    computed: {
        ...mapState('pages', ['current', 'total']),
        ...mapGetters('pages', ['range']),
        displayRange() {
            let output = []
            this.range.forEach(number => {
                // always show current page
                if (number == this.current) output.push(number)
                // for current page 1 or 2, display first 5
                else if (this.current <= 2 && number <= 5) output.push(number)
                // for current page last or next to last, display last 5
                else if (this.current + 1 >= this.total && number >= this.total - 4) output.push(number)
                // show the two numbers before and after the current page
                else if (this.current + 2 >= number && this.current - 2 <= number) output.push(number)
            })
            return output
        },
    },
    methods: {
        go(page) {
            this.$store.dispatch('pages/go', page)
        },
        next() {
            this.current < this.total && this.$store.dispatch('pages/next')
        },
        previous() {
            this.current > 1 && this.$store.dispatch('pages/previous')
        },
    },
})