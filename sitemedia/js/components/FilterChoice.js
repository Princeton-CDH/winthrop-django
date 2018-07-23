export default Vue.component ('FilterChoice', {
    template: `
    <label :active="active" is="sui-button" role="checkbox" basic circular>
        {{ label }}
        <input type="checkbox" :value="value" @input="$emit('input', $event.target.value)" :name="name" v-model="active">
    </label>
    `,
    props: {
        name: String,
        label: String,
        value: String
    },
    data() {
        return {
            active: false
        }
    }
})