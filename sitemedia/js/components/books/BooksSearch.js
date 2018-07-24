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
                :active="isActiveTab(index)"
                :content="tab.map(t => fieldLabels[t]).join(' · ')"
                @click="selectTab(index)"
            />
        </sui-menu>
        <sui-segment
            v-for="(tab, index) in tabs"
            :key="index"
            :class="{ active: isActiveTab(index) }"
            class="bottom attached tab"
        >
            <div class="ui equal width stackable grid">
                <search-facet
                    v-for="facet in tab"
                    v-bind="facets.filter(f => f.name===facet)"
                    @input="onStateChange"
                    :key="facet"
                    :label="fieldLabels[facet]"
                />
            </div>
        </sui-segment>
        <search-filter
            v-for="filter in filters"
            v-bind="filter"
            @input="onStateChange"
            :key="filter.label"
            :fieldLabels="fieldLabels"
        />
        <sui-segment inverted>
            <label>Selected</label>
            <div v-for="facet in activeFacets" :key="facet.name">
                <label>{{ fieldLabels[facet.name] }}:</label>
                <sui-label v-for="value in facet.value" :key="value">
                    {{ value }}
                    <sui-icon name="delete" />
                </sui-label>
            </div>
            <a v-if="activeFacets.length > 0">Clear All</a>
        </sui-segment>
    </form>`,
    components: {
        SearchFacet,
        SearchFilter
    },
    data() {
        return {
            formState: [],
            tabs: [
                ['author_exact', 'editor_exact', 'translator_exact'],
                ['publisher_exact', 'pub_year'],
                ['lang_exact', 'subject_exact'],
                ['annotator_exact']
            ],
            activeTab: 0,
            filters: [
                {
                    label: 'Only display',
                    choices: [
                        'is_annotated',
                        'is_digitized'
                    ]
                }
            ],
            fieldLabels: {
                'author_exact': 'Author',
                'editor_exact': 'Editor',
                'translator_exact': 'Translator',
                'publisher_exact': 'Publisher',
                'pub_year': 'Publication Year',
                'lang_exact': 'Language',
                'subject_exact': 'Subject',
                'annotator_exact': 'Annotator',
                'is_annotated': 'Annotated',
                'is_digitized': 'Digitized'
            },
            facets: initialData
        }
    },
    computed: {
        activeFacets() {
            return this.formState
                .filter(field => this.facets.map(facet => facet.name).includes(field.name))
                .map(field => ({name: field.name, value: this.toArray(field.value)}))
                .reduce(this.mergeFields, [])
        }
    },
    methods: {
        isActiveTab(tabIndex) {
            return this.activeTab === tabIndex
        },
        selectTab(tabIndex) {
            this.activeTab = tabIndex
        },
        onStateChange() {
            this.formState = $(this.$el).serializeArray()
        },
        /**
         * Utility that converts values to arrays.
         * If undefined, returns empty array.
         * If defined but not an array, returns value inside array.
         * If defined and an array, returns value unchanged.
         *
         * @param {*} v value to convert
         * @returns {Array}
         */
        toArray(v) {
            return v ? Array.isArray(v) ? v : [v] : []
        },
        /**
         * Reducer that merges values for form fields with the same name.
         * Expects that all values are already stored as arrays.
         *
         * @param {Array} acc the accumulator array
         * @param {Object} cur a field object from $.serializeArray()
         * @returns {Array}
         */
        mergeFields(acc, cur) {
            let f = acc.find(field => field.name == cur.name)
            if (f) f.value = f.value.concat(cur.value)
            else acc.push(cur)
            return acc
        }
    },
})