<template>
<div class="app">
  <CameraSurface>
    <button>Click me!</button>
  </CameraSurface>
</div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import CameraSurface from './components/CameraSurface.vue';

// console.log(mp);

export default defineComponent({
  name: 'App',
  components: {
    CameraSurface
  },
  data() {
    return {
    };
  },
  methods: {
  },
});
</script>

<style lang="scss">

body, html {
  margin: 0;
  padding: 0;
  background: #333;
}


</style>
