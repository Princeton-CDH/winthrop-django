import SemanticUIVue from 'semantic-ui-vue'
import BooksSearch from './components/books/BooksSearch'

$(() => {
    Vue.use(SemanticUIVue)
    
    new Vue({
        el: 'main',
        components: {
            BooksSearch
        }
    })
})
