import Vuex from 'vuex'
import mutations from './mutations'
import actions from './actions'
import getters from './getters'

Vue.use(Vuex)

const state = {
	facets: [],
	facetChoices: [],
	totalResults: 0,
	results: '',
	activeSort: '',
    keywordQuery: '',
    facetsEndpoint: '',
    resultsEndpoint: '',
}

export default new Vuex.Store({
	state,
	mutations,
	actions,
	getters,
})
