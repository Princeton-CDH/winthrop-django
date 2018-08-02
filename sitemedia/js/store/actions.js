import router from '../router'

export default {
    loadSearchData ({ commit, getters }) {
        return fetch(getters.dataPath)
            .then(res => res.json())
            .then(data => {
                commit('setTotalResults', data.total)
                Object.entries(data.facets).map(facet => {
                    Object.entries(facet[1]).map(choice => {
                        commit('addFacetChoice', {
                            facet: facet[0],
                            value: choice[0],
                            count: choice[1],
                            active: false,
                        })
                    })
                })
                Object.entries(data.range_facets).map(facet => {
                    commit('addRangeFacet', {
                        facet: facet[0],
                        minVal: undefined,
                        maxVal: undefined,
                    })
                    Object.entries(facet[1]).map(choice => {
                        commit('addFacetChoice', {
                            facet: facet[0],
                            value: choice[0],
                            count: choice[1],
                        })
                    })
                })
            })
    },

    updateFacetCounts ({ commit, getters }) {
        return fetch(getters.dataPath)
            .then(res => res.json())
            .then(data => {
                commit('setTotalResults', data.total)
                commit('updateFacetChoiceCounts', Object.entries(data.facets))
            })
    },

    toggleFacetChoice ({ commit, getters, dispatch }, choice) {
        let activeBeforeToggle = Object.keys(getters.activeFacets)
        commit('editFacetChoice', { choice, active: !choice.active })
        router.replace({
            query: {
                ...getters.activeFacets
            }
        })
        if (Object.keys(getters.activeFacets) != activeBeforeToggle) { // a facet was added or removed
            return dispatch('updateFacetCounts')
        }
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

    clearFacetChoices ({ commit }) {
        commit('clearFacetChoices')
        router.replace({
            path: '/'
        })
    },

    setFormState ({ commit, getters }, query) {
        if (JSON.stringify(query) != JSON.stringify(getters.activeFacets)) {
            commit('setFacetChoices', Object.entries(query))
        }
    }
}