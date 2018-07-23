import SearchFacet from '../SearchFacet'
import SearchFilter from '../SearchFilter'
import initialData from './initialData'

export default Vue.component('BooksSearch', {
    template: `
    <form class="search-form ui form">
        <sui-menu tabular attached="top">
            <div
                is="sui-menu-item"
                v-for="(tab, index) in tabs"
                :key="index"
                :active="isActive(index)"
                :content="tab.join(' · ')"
                @click="select(index)"
            />
        </sui-menu>
        <sui-segment
            v-for="(tab, index) in tabs"
            :key="index"
            :class="{ active: isActive(index) }"
            class="bottom attached tab"
        >
            <div class="ui equal width stackable grid">
                <search-facet
                    v-for="facet in tab"
                    v-bind="facets.filter(f => f.label===facet)"
                    @input="onStateChange"
                    :key="facet"
                    :label="facet"
                />
            </div>
        </sui-segment>
        <search-filter
            v-for="filter in filters"
            v-bind="filter"
            @input="onStateChange"
            :key="filter.label"
        />
        <sui-segment inverted>
            <label>Selected</label>
            {{ formState }}
        </sui-segment>
    </form>`,
    components: {
        SearchFacet,
        SearchFilter
    },
    data() {
        return initialData
    },
    computed: {
        // activeFilters() {
        //     return this.formState.filter(field => this.filters.map(filter => filter.label).includes(field.name)) 
        // },
        // activeFacets() {
        //     return this.formState.filter(field => this.facets.map(facet => facet.label).includes(field.name))
        // }
    },
    methods: {
        isActive(tabIndex) {
          return this.active === tabIndex
        },
        select(tabIndex) {
          this.active = tabIndex
        },
        onStateChange() {
            this.formState = $(this.$el).serializeArray()
        }
    },
})