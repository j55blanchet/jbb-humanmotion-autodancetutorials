<template>
  <div class="create-lesson-screen p-4 content">
    <teleport to="#topbarLeft">
      <button class="button" @click="$emit('back-selected')">&lt; Back</button>
    </teleport>

    <teleport to='#belowSurface'>
      <span class="is-pulled-right mt-4">
        <!-- <button class="button mr-2"  @click="playVideo">Play</button>
        <button class="button" @click="pauseVideo">Pause</button> -->
      </span>
    </teleport>

    <h3>Lesson Creation</h3>

    <VideoPlayer />
  </div>
</template>

<script lang="ts">

import {
  computed, defineComponent, ref,
} from 'vue';

import VideoPlayer from '@/components/elements/VideoPlayer.vue';

export default defineComponent({
  name: 'CreateLessonScreen',
  components: {
    VideoPlayer,
  },
  emits: ['back-selected', 'lesson-created'],
  data() {
    return {
    };
  },
  setup() {
  },
});
</script>

<style>

.create-lesson-screen {
  width: 1280px;
  height: 720px;
  position: relative;
  background: white;
  box-sizing: border-box;
}
</style>
