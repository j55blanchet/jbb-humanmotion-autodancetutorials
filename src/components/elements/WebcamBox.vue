<template>
  <div class="is-relative webcam-box">
    <video
      ref="videoE" muted disablePictureInPicture
      :style="{
        'max-height': maxHeight,
        'max-width': '100%',
      }"
    ></video>
    <div class="is-overlay" v-if="webcamStatus !== 'running'">
      <div class="vcenter-parent">
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
      </div>
    </div>
  </div>
</template>

<script lang="ts">

import {
  defineComponent, onBeforeUnmount, onMounted, ref, watch,
} from 'vue';

import webcamProvider from '@/services/WebcamProvider';

export default defineComponent({
  name: 'WebcamBox',
  props: {
    showStartWebcamButton: {
      type: Boolean,
      default: true,
    },
    enableRecordButton: {
      type: Boolean,
      default: false,
    },
    maxHeight: {
      type: String,
    },
  },
  setup() {
    // const enableRecordButton = toRefs(props);

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
      isRecording: webcamProvider.isRecording,
    };
  },
  computed: {
    webcamStarted() {
      return (this as any).webcamStatus === 'stopped';
    },
  },
  methods: {
    async startWebcam() {
      this.webcamStartError = null;

      try {
        await webcamProvider.startWebcam();
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

.webcam-box {

  max-width: 100%;
  max-height: 100%;

  video {
    background: rgba(128, 128, 128, 0.5);
    width: 1280px;
    // height: 720px;
    max-height: 100%;
    max-width: 100%;

    transform: scaleX(-1);
  }
}
</style>
