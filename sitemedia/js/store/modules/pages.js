export default {
    namespaced: true,
    state: {
        current: 1,
        total: 0,
    },
    mutations: {
        next: state => state.current++, // go to the next page
        previous: state => state.current--, // go to the previous page
        go: (state, page) => state.current = page, // go to a given page
        setTotal: (state, total) => state.total = total, // set the total number of pages
    },
    actions: {
        next: async ({ commit, dispatch }) => { // go to the next page and request results
            commit('next')
            await dispatch('results/update', null, { root: true })
        }, 
        previous: async ({ commit, dispatch }) => { // go to the previous page and request results
            commit('previous')
            await dispatch('results/update', null, { root: true })
        }, 
        go: async ({ commit, dispatch }, page) => { // go to a given page and request results
            commit('go', page)
            await dispatch('results/update', null, { root: true })
        },
    },
    getters: {
        range: state => [...Array(state.total + 1).keys()].slice(1), // [1, 2, ... total]
    },
}