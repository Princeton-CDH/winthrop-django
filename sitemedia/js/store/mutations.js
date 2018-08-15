import { toArray } from '../utilities'

export default {
    /**
     * Takes an object parsed from the solr JSON response
     * and populates the list of facets and choices.
     * 
     * Note that range facets and choices are included but have
     * a different schema, as they have different state.
     *
     * @param {Object} state current application state
     * @param {Object} data parsed solr response
     */
    addFacets: (state, { facets, range_facets }) => { // we assume the solr response has these keys
        for (const facet in facets) {
            state.facets.push({
                name: facet, // str, the name of the facet, e.g. "author"
                type: 'text',  // str, one of ['text', 'range']
            })
            for (const value in facets[facet]) {
                state.facetChoices.push({
                    facet: facet, // str, the name of the facet the choice belongs to, e.g. "author"
                    value: value, // str, the value of the choice, e.g. "John Smith"
                    count: facets[facet][value], // int, the number of results that have this facet value
                    active: false, // bool, whether the user has currently picked the choice
                })
            }
        }
        for (const facet in range_facets) {
            state.facets.push({
                name: facet, // str, the name of the range facet, e.g. "pub_date"
                type: 'range', // str, one of ['text', 'range']
                minName: `${facet}_0`, // solr uses _0 to indicate minimum
                maxName: `${facet}_1`, // solr uses _1 to indicate maximum
                minVal: undefined, // int, the lower bound of the range the user has currently chosen
                maxVal: undefined, // int, the upper bound of the range the user has currently chosen
            })
            for (const value in range_facets[facet]) {
                state.facetChoices.push({
                    facet: facet, // str, the name of the range facet the choice belongs to, e.g. "pub_date"
                    value: value, // int, the value of the choice, e.g. 1575
                    count: range_facets[facet][value], // int, the number of results that have this facet value
                })
            }
        }
    },

    /**
     * Toggles whether a single facet choice is active.
     *
     * @param {Object} state current application state
     * @param {Object} choice choice to toggle
     */
    toggleFacetChoice: (state, { facet, value }) => {
        let target = state.facetChoices
            .filter(choice => choice.facet === facet) // filter by facet first
            .find(choice => choice.value === value) // then find by value
        target.active = !target.active
    },

    /**
     * Deactivates all facet choices.
     *
     * @param {Object} state current application state
     */
    clearFacetChoices: state => state.facetChoices.forEach(choice => choice.active = false),

    /**
     * Sets the facets to an exact state by deactivating all facets,
     * then activating only those specified.
     * 
     * Used to set many facets simultaneously, e.g. as a result of 
     * the user pasting in the URL from a previous search.
     *
     * @param {Object} state current application state
     * @param {Object} facets facet state as parsed from the URL query params
     */
    setFacetChoices: (state, facets) => {
        state.facetChoices.forEach(choice => choice.active = false) // reset all facets first
        let rangeFacetNames = state.facets // define the set of available range facets
            .filter(facet => facet.type === 'range')
            .reduce((acc, cur) => {
                acc.push(cur.minName, cur.maxName)
                return acc
            }, [])
        for (const facet in facets) {
            if (rangeFacetNames.includes(facet)) { // it's a range facet
                let target = state.facets
                    .filter(f => f.type === 'range')
                    .find(f => facet.includes(f.name)) // 'pub_date_0' includes 'pub_date'
                if (facet.includes('_0')) target.minVal = facets[facet] // set a min
                if (facet.includes('_1')) target.maxVal = facets[facet] // set a max
            }
            else { // it's a text facet
                for (const value of toArray(facets[facet])) { // text facet values might not be an array yet
                state.facetChoices
                    .filter(choice => choice.facet === facet)
                    .find(choice => choice.value === value)
                    .active = true
                }
            }
        }
    },

    /**
     * Takes an object parsed from the solr JSON response
     * and updates the counts for all facet choices.
     *
     * @param {Object} state current application state
     * @param {Object} data parsed solr response
     */
    updateFacetChoiceCounts: (state, { facets, range_facets }) => {
        for (const facet in { ...facets, ...range_facets }) { // join the facets and range facets together
            for (const value in facets[facet]) {
                state.facetChoices
                    .filter(choice => choice.facet === facet)
                    .find(choice => choice.value === value)
                    .count = facets[facet][value]
            }
        }
    },

    /**
     * Changes the minimum value for a range facet.
     *
     * @param {Object} state current application state
     * @param {Object} payload facet name & value to use
     */
    editRangeFacetMin: (state, { name, minVal }) => {
        state.facets.find(facet => facet.name === name).minVal = minVal
    },

    /**
     * Changes the maximum value for a range facet.
     *
     * @param {Object} state current application state
     * @param {Object} payload facet name & value to use
     */
    editRangeFacetMax: (state, { name, maxVal }) => {
        state.facets.find(facet => facet.name === name).maxVal = maxVal
    },

    /**
     * Unsets both the minumum and maximum values for a range facet.
     *
     * @param {Object} state current application state
     * @param {String} name range facet name
     */
    clearRangeFacet: (state, name) => {
        let target = state.facets.find(facet => facet.name === name)
        target.minVal = undefined
        target.maxVal = undefined
    },

    /**
     * Unsets values of all range facets.
     *
     * @param {Object} state current application state
     */
    clearRangeFacets: state => {
        state.facets
            .filter(facet => facet.type === 'range')
            .forEach(facet => {
                facet.minVal = undefined
                facet.maxVal = undefined
        })
    },

    /**
     * Takes an object parsed from the solr JSON response
     * and updates the number of total results.
     *
     * @param {Object} state current application state
     * @param {Object} data parsed solr response
     */
    updateTotalResults: (state, { total }) => {
        state.totalResults = total
    },

    /**
     * Takes a string parsed from the Django HTML response
     * and updates the results.
     *
     * @param {Object} state current application state
     * @param {String} results HTML response parsed into string
     */
    updateResults: (state, results) => {
        state.results = results
    },
    
    /**
     * Changes the active sorting option for search results.
     *
     * @param {Object} state current application state
     * @param {String} option sorting option to switch to
     */
    changeSort: (state, option) => {
        state.activeSort = option
    },

    /**
     * Sets the active keyword query.
     *
     * @param {*} state
     * @param {*} query
     */
    setKeywordQuery: (state, query) => {
        state.keywordQuery = query
    },

    /**
     * Stores the endpoint at which the form should look to receive JSON
     * facet data from Solr.
     *
     * @param {Object} state current application state
     * @param {String} endpoint path to use, e.g. '/books/facets'
     */
    setFacetsEndpoint: (state, endpoint) => {
        state.facetsEndpoint = endpoint
    },

    /**
     * Stores the endpoint at which the form should look to receive HTML
     * result data from Django.
     *
     * @param {Object} state current application state
     * @param {String} endpoint path to use, e.g. '/books'
     */
    setResultsEndpoint: (state, endpoint) => {
        state.resultsEndpoint = endpoint
    },
}