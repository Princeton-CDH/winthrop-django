import router from '../router'

export default {
    loadSearchData ({ commit }, query) {
        return fetch(query)
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

    toggleFacetChoice ({ commit, getters }, choice) {
        commit('editFacetChoice', { choice, active: !choice.active })
        router.replace({
            query: {
                ...getters.activeFacets
            }
        })
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