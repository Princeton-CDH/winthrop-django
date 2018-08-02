import isEqual from 'lodash/isEqual'
import router from '../router'

const fetchOpts = {
    headers: { // this header is needed to signal ajax request to django
        'X-Requested-With': 'XMLHttpRequest'
    }
}

export default {
    async loadSearchData ({ commit, getters, dispatch }) {
        await fetch(getters.dataPath, fetchOpts)
            .then(res => res.json())
            .then(data => {
                commit('setTotalResults', data.total)
                commit('addFacets', data.facets)
                commit('addRangeFacets', data.range_facets)
            })
        await dispatch('loadResults')
    },

    async updateFacetChoiceCounts ({ commit, getters }) {
        await fetch(getters.dataPath, fetchOpts)
            .then(res => res.json())
            .then(data => {
                commit('setTotalResults', data.total)
                commit('updateFacetChoiceCounts', data.facets)
            })
    },

    async toggleFacetChoice ({ commit, getters, dispatch }, choice) {
        let activeBeforeToggle = Object.keys(getters.activeFacets)
        commit('editFacetChoice', { choice, active: !choice.active })
        dispatch('updateURL')
        if (!isEqual(Object.keys(getters.activeFacets), activeBeforeToggle)) { // a facet was added or removed
            await dispatch('updateFacetChoiceCounts')
        }
        await dispatch('loadResults')
    },

    async loadResults ({ commit, getters }) {
        await fetch(getters.dataPath, fetchOpts)
            .then(res => res.json())
            .then(data => commit('setTotalResults', data.total))
        await fetch(getters.resultsPath, fetchOpts)
            .then(res => res.text())
            .then(results => commit('loadResults', results))
    },

    updateURL({ getters }) {
        router.replace({
            query: {
                ...getters.activeFacets
            }
        })
    },

    setRangeFacetMin ({ commit }, facet) {
        commit('editRangeFacet', facet)
    },

    setRangeFacetMax ({ commit }, facet) {
        commit('editRangeFacet', facet)
    },

    setEndpoint ({ commit }, endpoint) {
        commit('setEndpoint', endpoint)
    },

    clearFacetChoices ({ commit, dispatch }) {
        commit('clearFacetChoices')
        dispatch('updateURL')
    },

    setFormState ({ commit, getters }, query) {
        if (!isEqual(query, getters.activeFacets)) { // only change form state if it's out of sync with URL
            commit('setFacetChoices', query)
        }
    }
}