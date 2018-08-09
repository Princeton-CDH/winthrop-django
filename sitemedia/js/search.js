import SemanticUIVue from 'semantic-ui-vue'
import VueRouter from 'vue-router'
import Vue2Filters from 'vue2-filters'
import { sync } from 'vuex-router-sync'

import store from './store'
import router from './router'

import BooksSearch from './components/books/BooksSearch'
import SearchResults from './components/SearchResults'
import { mapActions } from 'vuex'

const unsync = sync(store, router)

$(() => {
    Vue.use(VueRouter)
    Vue.use(SemanticUIVue)
    Vue.use(Vue2Filters)
    
    const searchInstance = new Vue({
        el: 'main',
        router,
        store,
        components: {
            BooksSearch,
            SearchResults
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
