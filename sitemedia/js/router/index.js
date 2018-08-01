import VueRouter from 'vue-router'

import store from '../store'
import BooksSearch from '../components/books/BooksSearch'

export const routes = [
    {
        path: '*', // always render the books search view
        component: BooksSearch,
        props: route => store.dispatch('setFormState', route.query) // convert any query params to form state
    } 
]

export default new VueRouter({
    routes,
    mode: 'history' // use the HTML5 history API
})