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
            })
    },

    toggleFacetChoice ({ commit }, choice) {
        commit('editFacetChoice', { choice, active: !choice.active })
    },

    clearFacetChoices ({ commit }) {
        commit('clearFacetChoices')
    },
}