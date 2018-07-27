export default {
    activeFacetChoices (state) {
        return state.facetChoices.filter(choice => choice.active)
    },
}