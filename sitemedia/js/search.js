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
import Pagination from './components/Pagination'
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
            Pagination,
            SearchResults,
        },
        beforeDestroy() {
            unsync() // clean up vuex-router sync
        },
        methods: {
            ...mapActions(['setKeywordQuery'])
        }
    })

    $('#site-search').sidebar('show') // open site search if it's not already
    window.queryStream.subscribe(searchInstance.setKeywordQuery) // update form with site search contents
    // don't allow enter key to submit the site search
    $('#site-search').keydown(e => { if (e.which === 13) e.preventDefault() })
})
