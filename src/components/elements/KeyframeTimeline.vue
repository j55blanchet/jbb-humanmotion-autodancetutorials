<template lang="jade">
  div
</template>

<script lang="ts">

import { defineComponent, Ref, toRefs, watchEffect } from 'vue';

export default defineComponent({
  name: 'KeyframeTimeline',
  props: {
    keyframes: {
      type: Array,
      default: () => [],
    },
    time: {
      type: Number,
      default: 0,
    },
  },
  setup(props) {
    const { keyframes, time } = toRefs(props);

    const keyframesTyped = keyframes as Ref<number[]>;

    watchEffect(() => {

      const keyframesLength = keyframesTyped.value.length;

    });

    return {
      // keyframes,
      // time,
    };
  },
});
</script>

<style lang="sass">

</style>
