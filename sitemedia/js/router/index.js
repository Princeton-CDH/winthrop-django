import VueRouter from 'vue-router'

export const routes = [{ path: '*' }]

export default new VueRouter({
    routes,
    mode: 'history' // use the HTML5 history API
})