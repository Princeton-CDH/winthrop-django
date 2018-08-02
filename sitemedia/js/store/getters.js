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
    },

    queryString (state) {
        return state.route.fullPath.split('?')[1]
    },

    dataPath (state, getters) {
        if (getters.queryString) {
            return `${state.route.path}${state.endpoint}?${getters.queryString}`
        }
        return `${state.route.path}${state.endpoint}`
    },

    resultsPath (state, getters) {
        if (getters.queryString) {
            return `${state.route.path}?${getters.queryString}`
        }
        return `${state.route.path}`
    }
}