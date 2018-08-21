import querystring from 'query-string'
import { ajax, parser } from '../../utilities'

export default {
    namespaced: true,
    state: {
        total: 0,
        activeSort: '',
        html: '',
        endpoint: '',
    },
    mutations: {
        sort: (state, sort) => state.activeSort = sort, // change active sort type
        update: (state, html) => state.html = html, // update the stored result HTML
        setTotal: (state, total) => state.total = total, // update the total number of results
        setEndpoint: (state, endpoint) => state.endpoint = endpoint, // update the endpoint at which to fetch results
    },
    actions: {
        update: async ({ commit, dispatch, getters, rootGetters }) => {
            await fetch(getters.path(rootGetters.formState), ajax) // get result data from the server
                .then(res => res.text())
                .then(html => {
                    let doc = parser.parseFromString(html, 'text/html') // parse the return HTML
                    let data = JSON.parse(doc.getElementById('results-data').innerHTML) // extract JSON pagination data
                    commit('setTotal', data.total) // set the total results
                    commit('pages/setTotal', data.pages, { root: true }) // root:true necessary to use other module
                    commit('update', html) // update the actual result HTML
                    dispatch('updateURL', null, { root: true }) // update the URL
                })
        },
        sort: async ({ commit, dispatch, getters, rootGetters }, sort) => {
            commit('sort', sort) // change the sort type
            commit('pages/go', 1) // go back to the first page
            await fetch(getters.path(rootGetters.formState), ajax) // get result data from the server
                .then(res => res.text()) // we don't need the pagination data because it stays the same
                .then(html => {
                    commit('update', html) // just update result HTML
                    dispatch('updateURL', null, { root: true }) // and the URL
                })
        },
    },
    getters: {
        path: state => formState => `${state.endpoint}?${querystring.stringify(formState)}`, // convert the form to a querystring and make a URL
    }
}