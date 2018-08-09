import isEqual from 'lodash/isEqual'
import router from '../router'

const fetchOpts = {
    headers: { // this header is needed to signal an ajax request to Django
        'X-Requested-With': 'XMLHttpRequest',
    }
}

export default {
    async addFacets ({ commit, getters }) {
        await fetch(getters.dataPath, fetchOpts)
            .then(res => res.json())
            .then(data => commit('addFacets', data))
    },

    async updateFacets ({ commit, getters }) {
        await fetch(getters.dataPath, fetchOpts)
            .then(res => res.json())
            .then(data => commit('updateFacetChoiceCounts', data))
    },
    
    async updateResults ({ commit, getters }) {
        await fetch(getters.dataPath, fetchOpts) // this is inefficient :(
            .then(res => res.json())
            .then(data => commit('updateTotalResults', data))
        await fetch(getters.resultsPath, fetchOpts)
            .then(res => res.text())
            .then(results => commit('updateResults', results))
    },
    
    async toggleFacetChoice ({ commit, dispatch }, choice) {
        commit('toggleFacetChoice', choice)
        dispatch('updateURL')
        await dispatch('updateFacets')
        await dispatch('updateResults')
    },
    
    async clearFacetChoices ({ commit, dispatch }) {
        commit('clearFacetChoices')
        dispatch('updateURL')
        await dispatch('updateFacets')
        await dispatch('updateResults')
    },

    async changeSort({ commit, dispatch }, option) {
        commit('changeSort', option)
        dispatch('updateURL')
        await dispatch('updateResults')
    },

    async setKeywordQuery({ state, commit, dispatch }, query) {
        commit('setKeywordQuery', query)
        if (!query && state.activeSort === 'relevance') { // if the query was deleted and we were on relevance, switch to author a-z
            commit('changeSort', 'author_asc')
        }
        dispatch('updateURL')
        await dispatch('updateFacets')
        await dispatch('updateResults')
    },
    
    updateURL({ getters }) {
        router.replace({ query: { ...getters.formState } })
    },

    setFormState ({ commit, getters }, query) { // TODO optimize this
        if (!isEqual(query, getters.formState)) { // only change form state if it's out of sync with URL
            commit('setFacetChoices', query)
            commit('setKeywordQuery', query.query)
            commit('changeSort', query.sort)
        }
    },
}