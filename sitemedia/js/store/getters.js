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
    },

    /**
     * Generate a representation of the current form state.
     * If no options are active, will return an empty object.
     *
     * @param {Object} state application state
     * @param {Object} getters other getter functions
     * @returns {Object} form state
     */
    formState (state, getters) {
        return {
            ...getters.activeFacets,
            ...(state.activeSort && {'sort': state.activeSort}), // we only add this property if it's defined
            ...(state.query && {'query': state.query}), // same here
        }
    },
}