import querystring from 'query-string'

import { toArray } from '../utilities'

export default {
    /**
     * Returns only the currently active facet choices.
     *
     * @param {Object} state application state
     * @returns {Array} active facet choices
     */
    activeFacetChoices: state => state.facetChoices.filter(choice => choice.active),

    /**
     * Reduces an array of range facets to an object
     * suitable for conversion into a URL querystring.
     *
     * @param {Object} state application state
     * @returns {Object} range facet state
     */
    activeRangeFacets: state => {
        return state.facets
            .filter(facet => facet.type === 'range')
            .reduce((acc, cur) => {
                if (cur.minVal) acc[cur.minName] = cur.minVal
                if (cur.maxVal) acc[cur.maxName] = cur.maxVal
                return acc
            }, {})
    },

    /**
     * Reduces an array of active facet choices to an object
     * suitable for conversion into a URL querystring.
     *
     * @param {Object} state application state
     * @param {Object} getters other getter functions
     * @returns {Object} facet state
     */
    activeFacets: (state, getters) => {
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

    /**
     * Returns a representation of the current form state.
     * If no options are active, will return an empty object.
     *
     * @param {Object} state application state
     * @param {Object} getters other getter functions
     * @returns {Object} form state
     */
    formState: (state, getters) => {
        return {
            ...getters.activeFacets,
            ...getters.activeRangeFacets,
            ...(state.activeSort && { 'sort': state.activeSort }), // we only add this property if it's defined
            ...(state.keywordQuery && { 'query': state.keywordQuery }), // same here
        }
    },

    /**
     * Returns a function that will create a URL to pass to fetch()
     * that will return JSON facet data from Solr.
     * 
     * Resulting function takes an optional argument that allows it to
     * generate a URL for any form state; default is the current state.
     *
     * @param {Object} state application state
     * @param {Object} getters other getter functions
     * @returns {Function} URL function
     */
    facetsPath: (state, getters) => formState => {
        if (formState) return `${state.facetsEndpoint}?${querystring.stringify(formState)}`
        else return `${state.facetsEndpoint}?${querystring.stringify(getters.formState)}`
    },

    /**
     * Returns a function that will create a URL to pass to fetch()
     * that will return HTML result data from Django.
     * 
     * Resulting function takes an optional argument that allows it to
     * generate a URL for any form state; default is the current state.
     *
     * @param {Object} state application state
     * @param {Object} getters other getter functions
     * @returns {Function} URL function
     */
    resultsPath: (state, getters) => formState => {
        if (formState) return `${state.resultsEndpoint}?${querystring.stringify(formState)}`
        else return `${state.resultsEndpoint}?${querystring.stringify(getters.formState)}`
    },
}