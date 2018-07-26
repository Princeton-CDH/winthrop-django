export default {
    loadFacetData ({ commit }, query) {
        return fetch(query)
            .then(res => res.json())
            .then(data => {
                commit('setTotalResults', data.total)
                let newFacets = {}
                for (let facet in data.facets) {
                    let choices = []
                    for (let value in data.facets[facet]) {
                        choices.push({
                            value: value,
                            count: data.facets[facet][value],
                            active: false
                        })
                    }
                    newFacets[facet] = choices
                }
                commit('setFacets', newFacets)
            })
    },

    toggleFacetChoice ({ commit }, facet, value) {
        commit('toggleFacetChoice', facet, value)
    },

    clearFacetChoices ({ commit }) {
        commit('clearFacetChoices')
    },
}