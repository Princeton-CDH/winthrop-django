export default {
    addFacetChoice (state, choice) {
        state.facetChoices.push(choice)
    },

    removeFacetChoice (state, choice) {
        state.facetChoices
            .filter(c => c.facet === choice.facet && c.value === choice.value)
            .forEach(c => {
                state.facetChoices.splice(state.facetChoices.indexOf(c), 1)
            })
    },

    editFacetChoice (state, { choice, active = choice.active, count = choice.count }) {
        state.facetChoices
            .filter(c => c.facet === choice.facet && c.value === choice.value)
            .forEach(c => {
                c.active = active
                c.count = count
            })
    },

    clearFacetChoices (state) {
        state.facetChoices.forEach(choice => choice.active = false)
    },

    setTotalResults (state, total) {
        state.totalResults = total
    },
}