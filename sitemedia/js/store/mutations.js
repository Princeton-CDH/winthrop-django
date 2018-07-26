export default {
    setFacets (state, facets) {
        state.facets = facets
    },

    toggleFacetChoice (state, choice) {
        let target = state.facets[choice.facet].find(c => c.value == choice.value)
        target.active = !target.active
    },
    
    clearFacetChoices (state) {
        for (let facet in state.facets) {
            state.facets[facet].forEach(choice => choice.active = false)
        }
    },

    setTotalResults (state, total) {
        state.totalResults = total
    },
}