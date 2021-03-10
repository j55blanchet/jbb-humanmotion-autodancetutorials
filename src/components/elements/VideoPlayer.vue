<template>
  <div class="is-relative video-player-container"
    :style="{
      width: width,
      height: height,
    }">
  <video :src="videoUrl"
         :style="{
           width: width,
           height: height,
          }" ref="videoElement"
          v-on:loadedmetadata="resizeCanvas">
  </video>
    <canvas class="is-overlay"
            ref="canvasElement">
    </canvas>
  </div>
</template>

<script lang="ts">
import {
  computed, defineComponent, toRefs, onMounted, onBeforeUnmount, ref, nextTick, Ref,
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

    const videoUrl = computed(() => videoBaseUrl?.value ?? '');

    const resizeCanvas = setupCanvasResizing(videoElement, canvasElement);

    return {
      videoUrl,
      resizeCanvas,
      videoElement,
      canvasElement,
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
