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
      @loadedmetadata="scheduleCanvasResizing"
    ></video>
    <canvas class="is-overlay" ref="canvasElement"> </canvas>
  </div>
</template>

<script lang="ts">
import { DrawPose } from '@/services/MediaPipe';
import { Landmark } from '@/services/MediaPipeTypes';
import {
  computed,
  defineComponent,
  toRefs,
  onMounted,
  onBeforeUnmount,
  ref,
  nextTick,
  Ref,
  watch,
} from 'vue';

function onResize(canvasE: HTMLCanvasElement, videoE: HTMLVideoElement, modified: Ref<boolean>) {
  nextTick(() => {
    if (!canvasE || !videoE) return;

    // eslint-disable no-param-reassign
    if (canvasE.width !== videoE.offsetWidth) {
      canvasE.width = videoE.offsetWidth;
      modified.value = true;
    }
    if (canvasE.height !== videoE.offsetHeight) {
      canvasE.height = videoE.offsetHeight;
      modified.value = true;
    };
  });
}

function setupCanvasResizing(
  videoElement: Ref<null | HTMLVideoElement>,
  canvasElement: Ref<null | HTMLCanvasElement>,
  modified: Ref<boolean>,
) {
  function resizeCanvas() {
    const videoE = videoElement.value;
    const canvasE = canvasElement.value;
    if (videoE && canvasE) onResize(canvasE, videoE, modified);
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
    from: number,
    to: number,
    speed: number,
  ) {
    // console.log(`VideoPlayer :: Starting playback from ${from} to ${to} @ ${speed.toPrecision(2)}`);

    // eslint-disable-next-line no-param-reassign
    startTime.value = from;
    // eslint-disable-next-line no-param-reassign
    endTime.value = to;

    const videoE = videoElement.value;
    if (!videoE) {
      console.error("VideoE is null - can't start playback");
      return;
    }

    videoE.pause();
    videoE.playbackRate = speed;
    videoE.currentTime = from;

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
    poseLandmarks: {
      type: Array,
      required: false,
      default: undefined,
    },
  },
  emits: [
    'playback-completed',
    'progress',
  ],
  setup(props, ctx) {
    const { videoBaseUrl, poseLandmarks } = toRefs(props);

    const videoElement = ref(null as null | HTMLVideoElement);
    const canvasElement = ref(null as null | HTMLCanvasElement);

    const startTime = ref(0);
    const endTime = ref(0);
    const videoUrl = computed(() => videoBaseUrl?.value ?? '');
    const canvasModified = ref(false);

    const resizeCanvas = setupCanvasResizing(videoElement, canvasElement, canvasModified);

    let prevTime = -1;
    let timerId = -1;
    function onTimeUpdated() {
      const vidElement = videoElement.value;
      if (!vidElement) return;

      const time = vidElement.currentTime;
      if (time === prevTime) return;
      prevTime = time;

      ctx.emit('progress', time);

      if (time + 1 / 60 >= endTime.value) {
        vidElement.pause();
        console.log('VideoPlauer :: playback-completed');
        ctx.emit('playback-completed');
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

    function drawPose(lms: Landmark[]) {
      const canvasE = canvasElement.value;
      if (!canvasE) return;
      const canvasCtx = canvasE.getContext('2d') as CanvasRenderingContext2D;

      canvasCtx.clearRect(0, 0, canvasE.width, canvasE.height);
      if (lms) DrawPose(canvasCtx, lms as Landmark[]);
    }
    watch(poseLandmarks, (lms) => {
      drawPose(lms as Landmark[]);
    });
    watch(canvasModified, (wasModified) => {
      if (wasModified) {
        drawPose(poseLandmarks.value as Landmark[]);
        canvasModified.value = false;
      }
    });

    function scheduleCanvasResizing() {
      setTimeout(() => {
        nextTick(resizeCanvas);
      }, 100);
    }


    return {
      videoUrl,
      resizeCanvas,
      videoElement,
      canvasElement,
      playVideo,
      endTime,
      scheduleCanvasResizing,
    };
  },
  methods: {
    setTime(time: number) {
      const videoE = this.videoElement;
      if (videoE) {
        videoE.currentTime = time;
      }
    },
  },
});
</script>

<style lang="scss">
.video-player-container {
  canvas {
    margin: auto;
  }

  video {
    border-radius: 0.25rem;
  }
}
</style>
