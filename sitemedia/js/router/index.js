import VueRouter from 'vue-router'

import BooksSearch from '../components/books/BooksSearch'

export const routes = [
    { path: '*', component: BooksSearch } // always render the books search view
]

export default new VueRouter({
    routes,
    mode: 'history' // use the HTML5 history API
})