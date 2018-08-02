import Vuex from 'vuex'
import mutations from './mutations'
import actions from './actions'
import getters from './getters'

Vue.use(Vuex)

const state = {
	filters: [],
	totalResults: 0,
	facetChoices: [],
	rangeFacets: [],
	endpoint: '',
	results: ``,
}

export default new Vuex.Store({
	state,
	mutations,
	actions,
	getters,
})
