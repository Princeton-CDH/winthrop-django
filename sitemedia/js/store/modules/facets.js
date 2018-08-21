import { reduceFacets } from '../../utilities'

export default {
    namespaced: true,
    state: {
        facets: [],
        choices: [],
        endpoint: '',
    },
    mutations: {
        add: (state, facets) => facets.forEach(state.facets.push), // add a list of facets
        addChoices: (state, choices) => choices.forEach(state.choices.push), // add a list of facet choices
        setEndpoint: (state, endpoint) => state.endpoint = endpoint, // update the endpoint at which to fetch data
    },
    getters: {
        text: state => state.facets.filter(facet => facet.type === 'text'),
        range: state => state.facets.filter(facet => facet.type === 'range'),
        activeChoices: state => state.choices.filter(choice => choice.active),
        textAsObject: (state, getters) => getters.activeChoices.reduce(reduceFacets, {}),
        /**
         * Returns a function that accepts form state and will create
         * a URL to pass to fetch() that will return facet data.
         *
         * @param {Object} state application state
         */
        path: state => formState => `${state.endpoint}?${querystring.stringify(formState)}`
    },
    modules: {
        text: {
            getters: {
                all: state => 
                active: (state, getters) => getters.text.filter()
            }
        }
    }
}