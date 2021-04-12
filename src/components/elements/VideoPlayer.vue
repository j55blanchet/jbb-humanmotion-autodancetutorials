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
        opacity: '' + videoOpacity,
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
import poseProvider, { PoseProvider } from '@/services/PoseProvider';
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

    if (canvasE.width !== videoE.offsetWidth) {
      // eslint-disable-next-line no-param-reassign
      canvasE.width = videoE.offsetWidth;
      // eslint-disable-next-line no-param-reassign
      modified.value = true;
    }
    if (canvasE.height !== videoE.offsetHeight) {
      // eslint-disable-next-line no-param-reassign
      canvasE.height = videoE.offsetHeight;
      // eslint-disable-next-line no-param-reassign
      modified.value = true;
    }
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

  function pauseVideo() {
    const videoE = videoElement.value;
    if (!videoE) {
      console.error("VideoE is null - can't start playback");
      return;
    }
    videoE.pause();
  }

  return { playVideo, pauseVideo };
}

export default defineComponent({
  name: 'VideoPlayer',
  props: {
    videoBaseUrl: String,
    width: String,
    height: String,
    drawPoseLandmarks: {
      type: Boolean,
      default: false,
    },
    videoOpacity: {
      type: Number,
      default: 1,
    },
    fps: {
      type: Number,
      default: 30,
    },
  },
  emits: [
    'playback-completed',
    'progress',
  ],
  setup(props, ctx) {
    const { videoBaseUrl, drawPoseLandmarks, fps } = toRefs(props);

    const videoElement = ref(null as null | HTMLVideoElement);
    const canvasElement = ref(null as null | HTMLCanvasElement);
    const canvasCtx = computed(() => canvasElement.value?.getContext('2d') as CanvasRenderingContext2D | null);

    const startTime = ref(0);
    const endTime = ref(0);
    const videoUrl = computed(() => videoBaseUrl?.value ?? '');
    const currentTime = ref(0);
    const canvasModified = ref(false);

    const resizeCanvas = setupCanvasResizing(videoElement, canvasElement, canvasModified);

    const poses = ref([] as Readonly<Array<Readonly<Array<Readonly<Landmark>>>>>);
    const cPose = computed(() => {
      const frame = Math.floor(currentTime.value * fps.value);
      const pose = poses.value[frame] ?? [];
      return pose;
    });

    let prevTime = -1;
    let timerId = -1;
    function onTimeUpdated() {
      const vidElement = videoElement.value;
      if (!vidElement) return;

      const time = vidElement.currentTime;
      if (time === prevTime) return;
      prevTime = time;

      currentTime.value = time;
      ctx.emit('progress', time);

      if (time + 1 / 60 >= endTime.value) {
        vidElement.pause();
        console.log('VideoPlayer :: playback-completed');
        ctx.emit('playback-completed');
        clearInterval(timerId);
        timerId = -1;
      }
    }

    const startProgressUpdating = () => {
      if (timerId !== -1) clearInterval(timerId);
      timerId = setInterval(onTimeUpdated, 1000 / 30);
    };

    const { playVideo, pauseVideo } = setupVideoPlaying(
      videoElement,
      startTime,
      endTime,
      startProgressUpdating,
    );

    function scheduleCanvasResizing() {
      setTimeout(() => {
        nextTick(resizeCanvas);
      }, 100);
    }

    // Update pose drawing
    function clearDrawing() {
      const canvasE = canvasElement.value;
      const drawCtx = canvasCtx.value;
      if (!canvasE || !drawCtx) return;
      drawCtx.clearRect(0, 0, canvasE.width, canvasE.height);
    }
    function drawPose(lms: Landmark[]) {
      const drawCtx = canvasCtx.value;
      if (!drawCtx) return;
      DrawPose(drawCtx, lms);
    }

    watch([videoBaseUrl, drawPoseLandmarks], async () => {
      if (!drawPoseLandmarks.value) {
        poses.value = [];
        return;
      }

      poses.value = await poseProvider.GetPose(videoBaseUrl?.value ?? '');
    });
    watch([canvasModified, cPose, drawPoseLandmarks], () => {
      canvasModified.value = false;
      clearDrawing();

      if (drawPoseLandmarks.value) {
        drawPose(cPose.value as any);
      }
    });

    return {
      videoUrl,
      resizeCanvas,
      videoElement,
      canvasElement,
      playVideo,
      pauseVideo,
      endTime,
      scheduleCanvasResizing,
      poses,
      currentTime,
      cPose,
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
