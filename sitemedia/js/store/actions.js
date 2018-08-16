import router from '../router'
import { ajax } from '../utilities'


export default {
    /**
     * Loads JSON facet data and creates the facets and their choices.
     * Will optionally pass a given form state to facetsPath().
     *
     * @param {Object} context vuex store
     * @param {Object} formState optional state to use 
     */
    async addFacets ({ commit, getters }, formState) {
        await fetch(getters.facetsPath(formState), ajax)
            .then(res => res.json())
            .then(data => commit('addFacets', data))
    },

    /**
     * Loads JSON facet data and updates the facet choice counts.
     *
     * @param {Object} context vuex store
     */
    async updateFacets ({ commit, getters }) {
        await fetch(getters.facetsPath(), ajax)
            .then(res => res.json())
            .then(data => commit('updateFacetChoiceCounts', data))
    },
    
    /**
     * Activates or deactivates a facet choice.
     *
     * @param {Object} context vuex store
     * @param {Object} choice choice to toggle
     */
    async toggleFacetChoice ({ commit, dispatch }, choice) {
        commit('toggleFacetChoice', choice)
        await dispatch('updateFacets')
        await dispatch('results/update')
        dispatch('updateURL')
    },
    
    /**
     * Changes the minimum value for a range facet.
     *
     * @param {Object} context vuex store
     * @param {Object} facet facet to edit
     */
    async editRangeFacetMin ({ commit, dispatch }, facet) {
        commit('editRangeFacetMin', facet)
        await dispatch('updateFacets')
        await dispatch('results/update')
        dispatch('updateURL')
    },

    /**
     * Changes the maximum value for a range facet.
     *
     * @param {Object} context vuex store
     * @param {Object} facet facet to edit
     */
    async editRangeFacetMax ({ commit, dispatch }, facet) {
        commit('editRangeFacetMax', facet)
        await dispatch('updateFacets')
        await dispatch('results/update')
        dispatch('updateURL')
    },
    
    /**
     * Clears all active facet choices, including range facets.
     *
     * @param {Object} context vuex store
     */
    async clearFacets ({ commit, dispatch }) {
        commit('clearFacetChoices')
        commit('clearRangeFacets')
        await dispatch('updateFacets')
        await dispatch('results/update')
        dispatch('updateURL')
    },

    /**
     * Changes the active keyword query.
     *
     * @param {Object} context vuex store
     * @param {String} query keyword query
     */
    async setKeywordQuery({ state, commit, dispatch }, query) {
        commit('setKeywordQuery', query)
        if (!query && state.activeSort === 'relevance') { // if the query was deleted and we were on relevance...
            commit('results/sort', 'author_asc') // ...switch to author a-z
        }
        await dispatch('updateFacets')
        await dispatch('results/update')
        dispatch('updateURL')
    },
    
    /**
     * Updates the URL querystring to match the form state.
     *
     * @param {Object} context vuex store
     */
    updateURL({ getters }) {
        router.replace({ query: { ...getters.formState } })
    },

    /**
     * Makes the form state match a provided state object.
     *
     * @param {Object} context vuex store
     * @param {String} state state object
     */
    async setFormState ({ commit, dispatch }, state) { // TODO optimize this
        let { query, sort, page, ...facets } = state // destructure into text query, sort, facets, page
        commit('setFacetChoices', facets)
        commit('setKeywordQuery', query)
        commit('results/sort', sort)
        commit('pages/go', page)
        await dispatch('updateFacets')
        await dispatch('results/update')
    },
}