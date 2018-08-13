import debounce from 'lodash/debounce'
import { mapActions } from 'vuex'

import SearchFacet from './SearchFacet'

export default Vue.component('RangeFacet', {
    extends: SearchFacet, // inherit default facet settings
    template: `
    <sui-grid-column :width="width" class="field">
        <label :for="label">{{ label }}</label>
        <div class="range-facet">
            <div class="inputs">
                <sui-input :placeholder="minVal" @input="setMin" type="number" :min="minVal" :max="maxVal"/>
                <label>to</label>
                <sui-input :placeholder="maxVal" @input="setMax" type="number" :min="minVal" :max="maxVal"/>
            </div>
            <div class="histogram">
            </div>
        </div>
    </sui-grid-column>
    `,
    computed: {
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
            'editRangeFacet'
        ]),
        setMin: debounce(function (val) {
            this.editRangeFacet({ name: this.name, minVal: val })
        }, 500),
        setMax: debounce(function (val) {
            this.editRangeFacet({ name: this.name, maxVal: val })
        }, 500),
    },
})