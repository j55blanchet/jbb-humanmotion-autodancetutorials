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

function setupVideoPlaying(
  videoElement: Ref<HTMLVideoElement | null>,
  startTime: Ref<number>,
  endTime: Ref<number>,
  startProgressUpdating: () => void,
) {
  function playVideo(
    start: number,
    end: number,
    speed: number,
  ) {
    console.log(`VideoPlayer :: Starting playback from ${start} to ${end} @ ${speed.toPrecision(2)}`);

    // eslint-disable-next-line no-param-reassign
    startTime.value = start;
    // eslint-disable-next-line no-param-reassign
    endTime.value = end;

    const videoE = videoElement.value;
    if (!videoE) {
      console.error("VideoE is null - can't start playback");
      return;
    }

    videoE.pause();
    videoE.playbackRate = speed;
    videoE.currentTime = start;

    nextTick(() => {
      startProgressUpdating();
      videoE.play();
    });
  }

  return { playVideo };
}

export default defineComponent({
  name: 'VideoPlayer',
  props: {
    videoBaseUrl: String,
    width: String,
    height: String,
  },
  setup(props, ctx) {
    const { videoBaseUrl } = toRefs(props);

    const videoElement = ref(null as null | HTMLVideoElement);
    const canvasElement = ref(null as null | HTMLCanvasElement);

    const startTime = ref(0);
    const endTime = ref(0);
    const videoUrl = computed(() => videoBaseUrl?.value ?? '');

    const resizeCanvas = setupCanvasResizing(videoElement, canvasElement);

    let prevTime = -1;
    let timerId = -1;
    function onTimeUpdated() {
      const vidElement = videoElement.value;
      if (!vidElement) return;

      const time = vidElement.currentTime;
      if (time === prevTime) return;
      prevTime = time;

      ctx.emit('video-progressed', time);

      if (time + 1 / 60 >= endTime.value) {
        vidElement.pause();
        console.log('playback-finished');
        ctx.emit('playback-finished');
        clearInterval(timerId);
        timerId = -1;
      }
    }

    const startProgressUpdating = () => {
      if (timerId !== -1) clearInterval(timerId);
      timerId = setInterval(onTimeUpdated, 1000 / 30);
    };

    const { playVideo } = setupVideoPlaying(
      videoElement,
      startTime,
      endTime,
      startProgressUpdating,
    );

    return {
      videoUrl,
      resizeCanvas,
      videoElement,
      canvasElement,
      playVideo,
      endTime,
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
