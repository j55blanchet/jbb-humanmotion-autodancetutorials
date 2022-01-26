<template>
  <div class="webcam-box-container">
    <video
      v-show="webcamStatus === 'running'"
      ref="videoE" muted disablePictureInPicture
      :style="{
        'max-width': '100%',
      }"
    ></video>
    <div v-if="webcamStatus !== 'running' && showStartWebcamButton" class="has-border-grey-lighter p-4">

      <WebcamSourceSelectionMenu
        v-model:audioDeviceId="audioDeviceId"
        v-model:videoDeviceId="videoDeviceId"
        @startWebcamClicked="selfStartWebcam"/>
      <!-- <div class="vcenter-parent">
        <div class="notification" v-if="this.webcamStartError !== null">
          {{this.webcamStartError}}
        </div>
        <button
          v-if="showStartWebcamButton"
          @click="startWebcam"
          class="button is-primary"
          v-show="webcamStatus !== 'running'"
          :class="{'is-loading': webcamStatus==='loading'}">
          Start Webcam
        </button>
      </div> -->

    </div>
  </div>
</template>

<script lang="ts">

import {
  defineComponent, onBeforeUnmount, onMounted, ref, watch,
} from 'vue';

import webcamProvider from '@/services/WebcamProvider';
import WebcamSourceSelectionMenu from '@/components/elements/WebcamSourceSelectionMenu.vue';

export default defineComponent({
  name: 'WebcamBox',
  components: {
    WebcamSourceSelectionMenu,
  },
  props: {
    showStartWebcamButton: {
      type: Boolean,
      default: true,
    },
    maxHeight: {
      type: String,
    },
  },
  setup() {
    const videoE = ref(null as null | HTMLVideoElement);
    const webcamStartError = ref(null as null | any);

    onMounted(() => {
      if (!videoE.value) throw new Error('videoE is null');
      if (webcamProvider.webcamStatus.value === 'running') {
        webcamProvider.connectVideoElement(videoE.value);
      }
    });
    watch(webcamProvider.webcamStatus, (status) => {
      if (status === 'running' && videoE.value) {
        webcamProvider.connectVideoElement(videoE.value);
      }
    });
    onBeforeUnmount(() => {
      if (!videoE.value) throw new Error('videoE is null');
      webcamProvider.disconnectVideoElement(videoE.value);
    });

    return {
      videoE,
      webcamStartError,
      webcamProvider,
      webcamStatus: webcamProvider.webcamStatus,

      audioDeviceId: ref(''),
      videoDeviceId: ref(''),
    };
  },
  computed: {
    webcamStarted() {
      return (this as any).webcamStatus === 'stopped';
    },
  },
  methods: {
    async selfStartWebcam() {
      await this.startWebcam(this.videoDeviceId, this.audioDeviceId);
    },
    async startWebcam(videoDeviceId: string, audioDeviceId: string) {
      this.webcamStartError = null;

      try {
        await webcamProvider.startWebcam(videoDeviceId, audioDeviceId);
      } catch (e) {
        this.webcamStartError = e;
        return e;
      }

      if (!this.videoE) throw new Error('videoE is null');
      await webcamProvider.connectVideoElement(this.videoE);

      return false;
    },
    playVideo() {
      if (!this.videoE) throw new Error('videoE is null');
      this.videoE.play();
    },
  },
});
</script>

<style lang="scss">

.webcam-box-container {

  position: relative;
  height: 100%;
  display: flex;
  flex-flow: column nowrap;
  justify-content: center;
  align-items: center;

  // max-width: 100%;

  video {
    background: rgba(128, 128, 128, 0.2);
    flex: 1 1 auto;
    max-height: 100%;
    // width: 1280px;
    // height: 720px;
    // max-height: 100%;
    // max-width: 100%;

    transform: scaleX(-1);
  }
}
</style>
