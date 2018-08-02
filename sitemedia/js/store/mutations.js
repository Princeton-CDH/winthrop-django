import { toArray } from '../utilities'

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

    setFacetChoices (state, facets) {
        state.facetChoices.forEach(choice => choice.active = false)
        facets.forEach(facet => {
            state.facetChoices
                .filter(choice => choice.facet === facet[0] && toArray(facet[1]).includes(choice.value))
                .forEach(choice => choice.active = true)
        })
    },

    updateFacetChoiceCounts (state, facets) {
        facets.forEach(facet => {
            Object.keys(facet[1]).forEach(value => {
                state.facetChoices.find(c => c.facet === facet[0] && c.value === value).count = facet[1][value]
            })
        })
    },

    addRangeFacet (state, facet) {
        state.rangeFacets.push(facet)
    },

    editRangeFacet (state, { facet, minVal = facet.minVal, maxVal = facet.maxVal }) {
        state.rangeFacets[facet.facet].minVal = minVal
        state.rangeFacets[facet.facet].maxVal = maxVal
    },

    setEndpoint (state, endpoint) {
        state.endpoint = endpoint
    },

    setTotalResults (state, total) {
        state.totalResults = total
    },
}