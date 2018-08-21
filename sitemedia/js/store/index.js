import Vuex from 'vuex'
import mutations from './mutations'
import actions from './actions'
import getters from './getters'

import pages from './modules/pages'
import results from './modules/results'

Vue.use(Vuex)

const state = {
	facets: [],
	facetChoices: [],
    keywordQuery: '',
    facetsEndpoint: '',
}

export default new Vuex.Store({
	state,
	mutations,
	actions,
    getters,
    modules: {
        pages: pages,
        results: results,
    }
})
