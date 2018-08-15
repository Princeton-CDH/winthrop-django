import router from '../router'

const fetchOpts = {
    headers: { // this header is needed to signal an ajax request to Django
        'X-Requested-With': 'XMLHttpRequest',
    }
}

export default {
    /**
     * Loads JSON facet data and creates the facets and their choices.
     * Will optionally pass a given form state to facetsPath().
     *
     * @param {Object} context vuex store
     * @param {Object} formState optional state to use 
     */
    async addFacets ({ commit, getters }, formState) {
        await fetch(getters.facetsPath(formState), fetchOpts)
            .then(res => res.json())
            .then(data => commit('addFacets', data))
    },

    /**
     * Loads JSON facet data and updates the facet choice counts.
     *
     * @param {Object} context vuex store
     */
    async updateFacets ({ commit, getters }) {
        await fetch(getters.facetsPath(), fetchOpts)
            .then(res => res.json())
            .then(data => commit('updateFacetChoiceCounts', data))
    },
    
    /**
     * Loads HTML result data and updates the results.
     * Will optionally pass a given form state to resultsPath().
     * 
     * @param {Object} context vuex store
     * @param {Object} formState optional state to use 
     */
    async updateResults ({ commit, getters }, formState) {
        await fetch(getters.facetsPath(), fetchOpts) // this is inefficient :(
            .then(res => res.json())
            .then(data => commit('updateTotalResults', data))
        await fetch(getters.resultsPath(formState), fetchOpts) // ideally we get total & pagination data with this request
            .then(res => res.text())
            .then(results => commit('updateResults', results))
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
        await dispatch('updateResults')
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
        await dispatch('updateResults')
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
        await dispatch('updateResults')
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
        await dispatch('updateResults')
        dispatch('updateURL')
    },

    /**
     * Changes the active sort option.
     *
     * @param {Object} context vuex store
     * @param {String} option option to choose
     */
    async changeSort({ commit, dispatch }, option) {
        commit('changeSort', option)
        await dispatch('updateResults') // only need results, don't need to update facets
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
            commit('changeSort', 'author_asc') // ...switch to author a-z
        }
        await dispatch('updateFacets')
        await dispatch('updateResults')
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
        let { query, sort, ...facets } = state // destructure into text query, sort, and facets
        commit('setFacetChoices', facets)
        commit('setKeywordQuery', query)
        commit('changeSort', sort)
        await dispatch('updateFacets')
        await dispatch('updateResults')
    },
}