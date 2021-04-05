<template>
  <div class="pose-drawer p-4 content">
    <teleport to="#topbarLeft">
      <button class="button" @click="$emit('back-selected')">&lt; Back</button>
    </teleport>

    <teleport to='#belowSurface'>
      <button class="button is-pulled-right mt-4" @click="playVideo">Play</button>
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

        <div class="notification is-danger" v-show="error">
          {{error}}
        </div>

        <div class="table-container" style="overflow:auto auto; max-height: 500px;">
          <table class="table is-fullwidth is-hoverable is-bordered" v-if="poseLandmarks">
            <thead>
              <tr>
                <th>id</th>
                <th>x</th>
                <th>y</th>
                <th>vis</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(lm, index) in poseLandmarks" :key="index">
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
        :poseLandmarks="poseLandmarks"
        ref="videoPlayer"
        @progress="onProgress"/>
      </div>
    </div>

  </div>
</template>

<script lang="ts">
import DanceEntry from '@/model/DanceEntry';
import dances from '@/services/MotionDatabase';
import {
  computed, defineComponent, ref,
} from 'vue';

import poseProvider from '@/services/PoseProvider';

import VideoPlayer from '@/components/elements/VideoPlayer.vue';
import { Landmark } from '@/services/MediaPipeTypes';

export default defineComponent({
  name: 'PoseDrawerTest',
  components: { VideoPlayer },
  data() {
    return {
      dances,
    };
  },
  setup() {
    const videoPlayer = ref(null as null | typeof VideoPlayer);
    const dropdownOpen = ref(false);
    const clipName = ref('');
    const videoSrc = computed(() => (clipName.value ? (`dances/${clipName.value}.mp4`) : ''));
    const videoTime = ref(0);
    const fps = ref(30);
    const error = ref(null as string | null);

    const poseFrames = ref([] as Landmark[][]);
    const poseLandmarks = computed(() => {
      const frame = Math.floor(fps.value * videoTime.value);
      const poseFrame = poseFrames.value[frame];
      return poseFrame ?? null;
    });

    async function loadDance(dance: DanceEntry) {
      error.value = null;
      poseFrames.value = [];
      dropdownOpen.value = false;
      clipName.value = dance.videoSrc.replace('dances/', '').replace('.mp4', '');
      fps.value = dance.lessons[0]?.fps ?? 30;

      try {
        poseFrames.value = await poseProvider.GetPose(clipName.value);
      } catch (e) {
        error.value = `${e}`;
      }
    }

    function playVideo() {
      const vidPlayer = videoPlayer.value;
      if (!vidPlayer) return;
      vidPlayer.playVideo(0, 1000, 0.5);
    }

    function onProgress(time: number) {
      videoTime.value = time;
    }

    return {
      videoPlayer,
      error,
      poseFrames,
      loadDance,
      dropdownOpen,
      clipName,
      videoSrc,
      poseLandmarks,
      playVideo,
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
