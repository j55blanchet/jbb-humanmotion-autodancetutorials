<template>
  <div class="pose-drawer p-4 content">
    <teleport to="#topbarLeft">
      <button class="button" @click="$emit('back-selected')">&lt; Back</button>
    </teleport>

    <h3>Pose Drawer Test</h3>

    <div class="dropdown" :class="{ 'is-active': dropdownOpen}">
      <div class="dropdown-trigger">
        <button class="button" @click="dropdownOpen = !dropdownOpen">
          <span>Select a dance</span>
          <span class="icon is-small">
            <i class="fas fa-angle-down" aria-hidden="true"></i>
          </span>
        </button>
      </div>
      <div class="dropdown-menu">
        <div class="dropdown-content">
          <a v-for="dance in dances"
                  :key="dance.title"
                  class="dropdown-item"
            @click="loadDance(dance)">
            {{dance.title}}
          </a>
        </div>
      </div>
    </div>

    <div class="columns">
      <div class="column">
        <h4 class="mt-4">{{clipName}}</h4>
        {{poses[0]}}
      </div>
      <div class="column">
        <VideoPlayer
        :videoBaseUrl="videoSrc"
        :height="'70%'"/>
      </div>
    </div>

  </div>
</template>

<script lang="ts">
import DanceEntry from '@/model/DanceEntry';
import dances from '@/services/MotionDatabase';
import { computed, defineComponent, ref } from 'vue';

import PoseProvider from '@/services/PoseProvider';

import VideoPlayer from '@/components/elements/VideoPlayer.vue';

export default defineComponent({
  name: 'PoseDrawerTest',
  components: { VideoPlayer },
  data() {
    return {
      dances,
    };
  },
  setup() {

    const dropdownOpen = ref(false);
    const poses = ref([] as unknown);
    const clipName = ref('');
    const videoSrc = computed(() => `dances/${clipName.value}.mp4`);

    async function loadDance(dance: DanceEntry) {
      poses.value = [];
      clipName.value = dance.videoSrc.replace('dances/', '').replace('.mp4', '');
      poses.value = await PoseProvider.getPose(clipName.value);
      dropdownOpen.value = false;
    }

    return {
      poses,
      loadDance,
      dropdownOpen,
      clipName,
      videoSrc,
    };
  },
});
</script>

<style>

.pose-drawer {
  width: 100%;
  height: 100%;
  position: relative;
  background: white;
}
</style>
