import { toArray } from '../utilities'

export default {
    activeFacetChoices (state) {
        return state.facetChoices.filter(choice => choice.active)
    },

    activeFacets (state, getters) {
        return getters.activeFacetChoices
            .reduce((acc, cur) => {
                if (acc[cur.facet]) {
                    if (!Array.isArray(acc[cur.facet])) {
                        acc[cur.facet] = toArray(acc[cur.facet])
                    }
                    acc[cur.facet].push(cur.value)
                }
                else acc[cur.facet] = cur.value
                return acc
            }, {})
    }
}