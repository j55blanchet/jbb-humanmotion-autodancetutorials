<template>
  <div class="layout-test">
    <VideoPlayer
      :videoBaseUrl="'videos/derulo.mp4'"
      :drawPoseLandmarks="true"
    />
  </div>
</template>

<script>
import { defineComponent } from 'vue';
import VideoPlayer from '@/components/elements/VideoPlayer.vue';

export default defineComponent({
  components: {
    VideoPlayer,
  },

});
</script>

<style lang="scss">

.layout-test {
  background: white;
  padding: 0;
  // margin: 0 auto;

  // width: 100vw;
  // height: calc(100vh - 32px);

  overflow: hidden;
  box-sizing: border-box;
  // height: 400px;
}
</style>
