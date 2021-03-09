<template>
<div class="app">
  <CameraSurface ref="cameraSurface"
  @tracking-attained="onTrackingAttained()">

    <template v-slot:background>
      <img v-show="state == 0" src="./assets/tiktokdances.jpg" alt="Background Image">

    </template>

    <template v-slot:ui>
      <DanceMenu />

      <div class="vcenter-parent" v-if="state == 1">
        <div class="card"
        v-if="state == 0">
          <div class="card-content">
            <h3>Welcome to the Dance Tutorial Machine!</h3>
            <p>You'll use gestures to control this app.</p>
          </div>
          <div class="card-footer">
            <a @click="startWebcam()" class="card-footer-item">Start Webcam</a>
          </div>
        </div>

        <div class="loader-wrapper" v-if="state == 1">
          <div class="loader is-loading"></div>
        </div>
      </div>

      <OnboardingUI v-if="state == 2" />
    </template>

  </CameraSurface>
</div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import CameraSurface from './components/CameraSurface.vue';
import OnboardingUI from './components/OnboardingUI.vue';
import DanceMenu from './components/screens/DanceMenu.vue';

enum State {
  Initial,
  TrackingStarting,
  TrackingNormally
}

export default defineComponent({
  name: 'App',
  components: {
    CameraSurface,
    OnboardingUI,
    DanceMenu,
  },
  data() {
    return {
      state: State.Initial,
    };
  },
  methods: {
    startWebcam() {
      console.log('Starting Webcam');
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const camSurface: any = this.$refs.cameraSurface;
      camSurface.startTracking();
      this.state = State.TrackingStarting;
    },
    onTrackingAttained() {
      console.log('Tracking attained');
      this.state = State.TrackingNormally;
    },
  },
});
</script>

<style lang="scss">

body, html {
  margin: 0;
  padding: 0;
  background: #333;
}

.card {
  display: inline-block;
}

.vcenter-parent {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
}

.loader-wrapper {
  width: 200px;
  height: 200px;
  background: rgba(0, 0, 0, 0.3);
  padding: 3em;
  border-radius: 9999px;

  .loader {
    width: 100%;
    height: 100%;
  }
}
</style>
