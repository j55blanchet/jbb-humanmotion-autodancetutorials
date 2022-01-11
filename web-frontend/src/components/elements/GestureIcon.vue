<template>
  <span class="icon is-large" :class="iconClass" v-if="showIcon">
    <i class="fas fa-2x fa-hand-paper fa-rotate-90"></i>
  </span>
  <span v-else>
    <img :src="gestureImgSrc" :alt="gesture">
  </span>
</template>

<script lang="ts">
import { usingHolistic } from '@/services/MediaPipe';
import { computed, defineComponent, toRefs } from 'vue';

export const GestureIcons = Object.freeze({
  forward: 'forward',
  backward: 'backward',
  play: 'play',
});

export default defineComponent({
  props: {
    gesture: {
      type: String,
      default: 'foward',
    },
  },
  setup(props) {

    const { gesture } = toRefs(props);

    const showIcon = computed(() => usingHolistic);
    const iconClass = computed(() => {
      switch (gesture.value) {
        case 'backward': return ['fa-flip-horizontal'];
        case 'forward': return [];
        default:
          return [];
      }
    });
    /* eslint-disable global-require */
    /* eslint-disable import/no-dynamic-require */
    const gestureImgSrc = computed(() => {
      try {
        return require(`../../assets/gestures/${gesture.value}.svg`);
      } catch {
        return '';
      }
    });

    return {
      showIcon,
      iconClass,
      gestureImgSrc,
    };
  },
});
</script>

<style>
</style>
