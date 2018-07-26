export default {
    activeFacets (state) {
        return Object.entries(state.facets)
            .map(facet => facet[1].filter(choice => choice.active))
            .reduce((acc, cur) => Object.assign({ [cur[0]]: cur[1] }, acc), {})
    },
}