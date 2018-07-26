import SemanticUIVue from 'semantic-ui-vue'
import VueRouter from 'vue-router'
import Vue2Filters from 'vue2-filters'
import { sync } from 'vuex-router-sync'

import store from './store'
import router from './router'

import BooksSearch from './components/books/BooksSearch'

const unsync = sync(store, router)

$(() => {
    Vue.use(VueRouter)
    Vue.use(SemanticUIVue)
    Vue.use(Vue2Filters)
    
    new Vue({
        el: 'main',
        router,
        store,
        components: {
            BooksSearch
        },
        beforeDestroy() {
            unsync() // clean up vuex-router sync
        }
    })
})
