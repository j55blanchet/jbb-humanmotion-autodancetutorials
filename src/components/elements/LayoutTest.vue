<template>
  <div class="layout-test">
    <PausingVideoPlayer
      :videoSrc="'videos/derulo.mp4'"
      :drawPoseLandmarks="true"
    />
  </div>
</template>

<script>
import { defineComponent } from 'vue';
import PausingVideoPlayer from '@/components/elements/PausingVideoPlayer.vue';

export default defineComponent({
  components: {
    PausingVideoPlayer,
  },

});
</script>

<style lang="scss">

.layout-test {
  background: white;
  padding: 0;
  // margin: 0 auto;

  width: 100vw;
  height: calc(100vh - 32px);

  overflow: hidden;
  box-sizing: border-box;
  // height: 400px;
}
</style>
