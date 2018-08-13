import SemanticUIVue from 'semantic-ui-vue'
import VueRouter from 'vue-router'
import Vue2Filters from 'vue2-filters'
import { sync } from 'vuex-router-sync'
import { mapActions } from 'vuex'

import store from './store'
import router from './router'

import SearchForm from './components/SearchForm'
import TextFacet from './components/TextFacet'
import RangeFacet from './components/RangeFacet'
import SearchSort from './components/SearchSort'
import SearchResults from './components/SearchResults'

const unsync = sync(store, router)

$(() => {
    Vue.use(VueRouter) // for altering querystring programmatically
    Vue.use(SemanticUIVue) // for tabs and dropdown behavior
    Vue.use(Vue2Filters) // for "pluralize" filter for total results
    
    const searchInstance = new Vue({
        el: 'main',
        router,
        store,
        components: {
            SearchForm,
            TextFacet,
            RangeFacet,
            SearchSort,
            SearchResults,
        },
        beforeDestroy() {
            unsync() // clean up vuex-router sync
        },
        methods: {
            ...mapActions(['setKeywordQuery'])
        }
    })

    window.queryStream.subscribe(searchInstance.setKeywordQuery)
})
