<template>
  <div>
    <h1 class="title">Input Device Selection</h1>
    <div v-if="state === 'unloaded'" class="mt-4" style="max-width:60ch">
      <p class="block mt-4">We need your permission to list options for your webcam &amp; microphone. Click &quot;Load Devices&quot;, select the devices you wish to use, and click &quot;Start Webcam&quot;</p>
      <button class="block button is-primary" @click="loadDevices">Load Devices</button>
      <div class="block notification is-warning" v-if="error !== null">
        <p class="block"><strong>Error:</strong> <span class="is-family-monospace">{{error}}</span></p>
        <p class="block">Check that your webcam is connected, no other application is using your webcam, and that you have granted permission in your browser.</p>
      </div>
    </div>
    <div class="menu" v-else>
      <p class="menu-label">Video Devices</p>
      <ul class="menu-list">
        <li v-for="device in videoDevices" :key="device.deviceId">
          <a @click="selectVideoDevice(device.deviceId)"
             :class="{'is-active': videoDeviceId === device.deviceId}"
          >
            {{device.label}}
          </a>
        </li>
        <li v-if="state === 'loaded' && videoDevices.length === 0">No devices available.</li>
        <li v-if="state === 'loading'">Loading...</li>
      </ul>
      <p class="menu-label">Audio Devices</p>
      <ul class="menu-list">
        <li v-for="device in audioDevices" :key="device.deviceId">
          <a @click="selectAudioDevice(device.deviceId)"
             :class="{'is-active': audioDeviceId === device.deviceId}"
          >
            {{device.label}}
          </a>
        </li>
        <li v-if="state === 'loaded' && videoDevices.length === 0">No devices available.</li>
        <li v-if="state === 'loading'">Loading...</li>
      </ul>
    </div>
    <p v-if="state === 'loaded'" class="notification has-text-centered mt-4" style="max-width:60ch;margin:auto;">
      <span class="icon"><i class="fas fa-info-circle"></i></span> Click &quot;Start Webcam&quot; when you&rsquo;re ready.
    </p>
  </div>
</template>

<script lang="ts">
import { defineComponent, onMounted, ref } from 'vue';

export default defineComponent({
  name: 'WebcamSourceSelectionMenu',
  props: ['videoDeviceId', 'audioDeviceId'],
  emits: ['update:videoDeviceId', 'update:audioDeviceId'],
  setup(props, { emit }) {
    const videoDevices = ref([] as MediaDeviceInfo[]);
    const audioDevices = ref([] as MediaDeviceInfo[]);
    const state = ref('unloaded' as 'unloaded' | 'loading' | 'loaded');
    const error = ref(null as any | null);

    const selectVideoDevice = (id: string) => {
      emit('update:videoDeviceId', id);
    };
    const selectAudioDevice = (id: string) => {
      emit('update:audioDeviceId', id);
    };

    const loadDevices = async () => {
      try {
        error.value = null;
        await navigator.mediaDevices.getUserMedia({ audio: true, video: true });

        const devices = await navigator.mediaDevices.enumerateDevices();
        videoDevices.value = devices.filter((device) => device.kind === 'videoinput');
        audioDevices.value = devices.filter((device) => device.kind === 'audioinput');

        // Autoselect the first devices
        if (videoDevices.value.length > 0) {
          selectVideoDevice(videoDevices.value[0].deviceId);
        }
        if (audioDevices.value.length > 0) {
          selectAudioDevice(audioDevices.value[0].deviceId);
        }

        state.value = 'loaded';
      } catch (e) {
        state.value = 'unloaded';
        error.value = e;
      }
    };

    return {
      state,
      error,
      videoDevices,
      audioDevices,
      loadDevices,
      selectVideoDevice,
      selectAudioDevice,
    };
  },
});
</script>

<style lang="scss">

</style>
