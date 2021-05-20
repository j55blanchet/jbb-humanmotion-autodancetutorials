<template>
  <div class="activity-video-">
    <PausingVideoPlayer />
    <InstructionCarousel />
    <WebcamBox />
  </div>
</template>

<script lang="ts">

import {
  computed, ComputedRef, defineComponent, nextTick, onBeforeUnmount, onMounted, Ref, ref, toRefs, watch,
} from 'vue';
import InstructionCarousel, { Instruction } from '@/components/elements/InstructionCarousel.vue';
import PausingVideoPlayer from '@/components/elements/PausingVideoPlayer.vue';
import WebcamBox from '@/components/elements/WebcamBox.vue';

const ActivityPlayState = Object.freeze({
  AwaitingPlayGesture: 'AwaitingPlayGesture',
  PendingStart: 'PendingStart',
  Playing: 'Playing',
  ActivityEnded: 'ActivityEnded',
});

export default defineComponent({
  name: 'ActivityVideoPlayer',
  props: {
    dance: { type: Object },
    lesson: { type: Object },
    activity: { type: Object },
    defaultPauseDuration: { type: Number, default: 1.5 },
  },
  components: {
    PausingVideoPlayer,
    InstructionCarousel,
    WebcamBox,
  },
});

</script>

<style>

</style>
