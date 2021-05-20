<template>
  <div class="pose-drawer p-4 content">
    <teleport to="#topbarLeft">
      <button class="button" @click="$emit('back-selected')">&lt; Back</button>
    </teleport>

    <teleport to='#belowSurface'>
      <span class="is-pulled-right mt-4">
        <button class="button mr-2"  @click="playVideo">Play</button>
        <button class="button" @click="pauseVideo">Pause</button>
      </span>
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
          <a v-for="motion in motions"
                  :key="motion.title"
                  class="dropdown-item"
            @click="loadMotion(motion)">
            {{motion.title}}
          </a>
        </div>
      </div>
    </div>

    <div class="columns">
      <div class="column">
        <h4 class="mt-4">{{clipName}}</h4>

        <div class="notification is-danger" v-show="error">
          {{error}}
        </div>

        <div class="table-container" style="overflow:auto auto; max-height: 500px;">
          <table class="table is-fullwidth is-hoverable is-bordered" v-if="videoPlayer && videoPlayer.cPose">
            <thead>
              <tr>
                <th>id</th>
                <th>x</th>
                <th>y</th>
                <th>vis</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(lm, index) in videoPlayer.cPose" :key="index">
                <td>{{index}}</td>
                <td>{{lm.x}}</td>
                <td>{{lm.y}}</td>
                <td>{{lm.visibility}}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <div class="column is-one-third">
        <VideoPlayer
        :videoBaseUrl="videoSrc"
        :height="'500px'"
        ref="videoPlayer"
        :drawPoseLandmarks="true"
        @progress="onProgress"/>
      </div>
    </div>

  </div>
</template>

<script lang="ts">
import db, { DatabaseEntry } from '@/services/MotionDatabase';
import {
  computed, defineComponent, ref,
} from 'vue';

import VideoPlayer from '@/components/elements/VideoPlayer.vue';

export default defineComponent({
  name: 'PoseDrawerTest',
  components: { VideoPlayer },
  setup() {
    const { motions } = db;
    const videoPlayer = ref(null as null | typeof VideoPlayer);
    const dropdownOpen = ref(false);
    const clipName = ref('');
    const videoSrc = computed(() => (clipName.value ? (`dances/${clipName.value}.mp4`) : ''));
    const videoTime = ref(0);
    const fps = ref(30);
    const error = ref(null as string | null);

    async function loadMotion(motion: DatabaseEntry) {
      error.value = null;
      dropdownOpen.value = false;
      clipName.value = motion.clipName;
      fps.value = motion.fps;
    }

    function playVideo() {
      const vidPlayer = videoPlayer.value;
      if (!vidPlayer) return;
      vidPlayer.playVideo(0, 1000, 0.5);
    }
    function pauseVideo() {
      const vidPlayer = videoPlayer.value;
      if (!vidPlayer) return;
      vidPlayer.pauseVideo();
    }

    function onProgress(time: number) {
      videoTime.value = time;
    }

    return {
      motions,
      videoPlayer,
      error,
      loadMotion,
      dropdownOpen,
      clipName,
      videoSrc,
      playVideo,
      pauseVideo,
      onProgress,
    };
  },
});
</script>

<style>

.pose-drawer {
  width: 1280px;
  height: 720px;
  position: relative;
  background: white;
  box-sizing: border-box;
}
</style>
