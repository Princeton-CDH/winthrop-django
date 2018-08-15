import debounce from 'lodash/debounce'
import { mapActions, mapGetters } from 'vuex'

import SearchFacet from './SearchFacet'

export default Vue.component('RangeFacet', {
    extends: SearchFacet, // inherit default facet settings
    template: `
    <sui-grid-column :width="width" class="field">
        <label :for="label">{{ label }}</label>
        <div class="range-facet">
            <div class="inputs">
                <sui-input :placeholder="minVal" @input="setMin" type="number" :min="minVal" :max="maxVal" :value="rangeFacetMinMax(name).minVal"/>
                <label>to</label>
                <sui-input :placeholder="maxVal" @input="setMax" type="number" :min="minVal" :max="maxVal" :value="rangeFacetMinMax(name).maxVal"/>
            </div>
            <div class="histogram">
            </div>
        </div>
    </sui-grid-column>
    `,
    computed: {
        ...mapGetters([
           'rangeFacetMinMax', 
        ]),
        /**
         * Calculate the lowest valid value for the facet.
         *
         * @returns {Number}
         */
        minVal() {
            return this.choices
                .map(choice => parseInt(choice.value))
                .reduce((acc, cur) => cur < acc ? cur : acc, Infinity)
        },
        /**
         * Calculate the highest valid value for the facet.
         *
         * @returns {Number}
         */
        maxVal() {
            return this.choices
                .map(choice => parseInt(choice.value))
                .reduce((acc, cur) => cur > acc ? cur : acc, -Infinity)
        }
    },
    methods: {
        ...mapActions([
            'editRangeFacetMin',
            'editRangeFacetMax',
        ]),
        setMin: debounce(function (val) {
            this.editRangeFacetMin({ name: this.name, minVal: val })
        }, 1000),
        setMax: debounce(function (val) {
            this.editRangeFacetMax({ name: this.name, maxVal: val })
        }, 1000),
    },
})