<template>
    <div class="search-results" v-html="results"></div>
</template>

<script>
import { mapState } from 'vuex'

export default {
    computed: {
        ...mapState([
            'results',
        ]),
    }
}
</script>