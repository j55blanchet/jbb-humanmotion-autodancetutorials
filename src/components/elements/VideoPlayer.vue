<template>
  <div
    class="is-relative video-player-container"
    :style="{
      width: width,
      height: height,
    }"
  >
    <video
      :src="videoUrl"
      :style="{
        width: width,
        height: height,
      }"
      ref="videoElement"
      v-on:loadedmetadata="resizeCanvas"
      @timeupdate="onTimeUpdated"
    ></video>
    <canvas class="is-overlay" ref="canvasElement"> </canvas>
  </div>
</template>

<script lang="ts">
import {
  computed,
  defineComponent,
  toRefs,
  onMounted,
  onBeforeUnmount,
  ref,
  nextTick,
  Ref,
} from 'vue';

function onResize(canvasE: HTMLCanvasElement, videoE: HTMLVideoElement) {
  nextTick(() => {
    if (!canvasE || !videoE) return;

    // eslint-disable-next-line no-param-reassign
    if (canvasE.width !== videoE.offsetWidth) canvasE.width = videoE.offsetWidth;
    // eslint-disable-next-line no-param-reassign
    if (canvasE.height !== videoE.offsetHeight) canvasE.height = videoE.offsetHeight;
  });
}

function setupCanvasResizing(
  videoElement: Ref<null | HTMLVideoElement>,
  canvasElement: Ref<null | HTMLCanvasElement>,
) {
  function resizeCanvas() {
    const videoE = videoElement.value;
    const canvasE = canvasElement.value;
    if (videoE && canvasE) onResize(canvasE, videoE);
  }
  onMounted(() => {
    window.addEventListener('resize', resizeCanvas);
    nextTick(resizeCanvas);
  });
  onBeforeUnmount(() => {
    window.removeEventListener('resize', resizeCanvas);
  });
  return resizeCanvas;
}

export default defineComponent({
  name: 'VideoPlayer',
  props: {
    videoBaseUrl: String,
    width: String,
    height: String,
  },
  setup(props) {
    const { videoBaseUrl } = toRefs(props);

    const videoElement = ref(null as null | HTMLVideoElement);
    const canvasElement = ref(null as null | HTMLCanvasElement);

    const startTime = ref(0);
    const endTime = ref(0);
    const videoUrl = computed(() => videoBaseUrl?.value ?? '');

    const resizeCanvas = setupCanvasResizing(videoElement, canvasElement);

    // eslint-disable-next-line @typescript-eslint/no-empty-function
    const noop = () => {};
    // eslint-disable-next-line max-len
    // eslint-disable-next-line @typescript-eslint/no-empty-function, @typescript-eslint/no-unused-vars
    const noopParam = (time: number) => {};

    const playCallbacks = {
      finished: noop,
      timeUpdated: noopParam,
    };

    function playVideo(
      start: number,
      end: number,
      speed: number,
      onFinished: () => void,
      timeUpdated?: (time: number) => void,
    ) {
      console.log(`VideoPlayer :: Starting playback from ${start} to ${end} @ ${speed.toPrecision(2)}`);
      startTime.value = start;
      endTime.value = end;

      const videoE = videoElement.value;
      if (!videoE) {
        console.error("VideoE is null - can't start playback");
        return;
      }

      videoE.playbackRate = speed;

      playCallbacks.finished = onFinished;
      // eslint-disable-next-line @typescript-eslint/no-empty-function
      playCallbacks.timeUpdated = timeUpdated || noopParam;

      videoE.play();
    }

    function onTimeUpdated() {
      const vidElement = videoElement.value;
      if (!vidElement) return;

      playCallbacks.timeUpdated(vidElement.currentTime);

      console.log('TimeUpdated', vidElement.currentTime);

      if (vidElement.currentTime > endTime.value) {
        vidElement.pause();
        playCallbacks.finished();
      }
    }

    return {
      videoUrl,
      resizeCanvas,
      videoElement,
      canvasElement,
      playVideo,
      onTimeUpdated,
    };
  },
});
</script>

<style lang="scss">
.video-player-container {
  canvas {
    margin: auto;
  }
}
</style>
