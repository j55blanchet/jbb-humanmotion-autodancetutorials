<template>
  <section class="keyframe-selection section">
    <div class="container box">
      <h1 class="title">Keyframe Selection Tool</h1>

      <div class="buttons">
        <button class="button" @click="$emit('back-selected')">&lt; Back</button>
      </div>

      <div class="block">
        <video
          ref="videoElement"
          @playing="paused = false"
          @pause="paused = true"
          @seeked="updateCurrentTime"
          :src="videoEntry.videoSrc"
          style="max-height: 50vh; max-width: 768px;"></video>
      </div>

      <div class="buttons is-grouped">
        <button class="button" @click="videoElement.currentTime -= 0.1">&lt;&lt;</button>
        <button class="button" @click="videoElement.currentTime -= 0.03">&lt;</button>
        <span class="button is-text" disabled>
          {{currentTime.toFixed(2)}}s
        </span>
        <button class="button" @click="addKeyframe">&plus; Add</button>
        <button class="button" @click="videoElement.currentTime += 0.03">&gt;</button>
        <button class="button" @click="videoElement.currentTime += 0.1">&gt;&gt;</button>
      </div>

      <div class="block">
        <pre>{{JSON.stringify(keyframes)}}</pre>
      </div>

      <div class="block">
        <h3 class="subtitle">Keyframes</h3>
        <div class="is-flex is-flex-wrap-wrap">
          <div
              :class="{'is-active': frameInfo.isCurrent}"
              class="keyframe is-relative  over-expand is-clickable"
              v-for="(frameInfo, i) in keyframesWithVideo"
              :key="i"
              @click="deleteKeyframe(frameInfo.kf)">

            <!-- <div class="has-text-right is-overlay"><button class="button is-small is-danger is-light">&times;</button></div> -->
            <video class="keyframe-thumb"
            :src="videoEntry.videoSrc + '#t=' + frameInfo.kf">
            </video>
            <div class="has-text-centered mb-2"><span class="tag">{{frameInfo.kf.toFixed(2)}}</span></div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script lang="ts">
import {
  defineComponent, onBeforeUnmount, onMounted, ref, toRefs, watchEffect,
} from 'vue';
import motionDb, { DatabaseEntry } from '@/services/MotionDatabase';

// [2.28,2.73,2.93,3.18,3.26,3.47,3.54,3.69,4.02,4.2,4.35,4.53,4.71,4.98,5.13,5.44,5.53]
export default defineComponent({
  name: 'KeyframeSelectorTool',
  emits: ['back-selected', 'update:modelValue'],
  props: {
    videoEntry: {
      type: Object,
      required: true,
    },
    modelValue: {
      type: Array,
      default: Array,
    },
  },
  setup(props) {
    const { modelValue } = toRefs(props);
    const paused = ref(false);
    const currentTime = ref(0);
    const videoElement = ref(null as HTMLVideoElement | null);

    const updateCurrentTime = () => { currentTime.value = videoElement.value?.currentTime ?? 0; };
    let updateIntervalId = -1;
    onBeforeUnmount(() => { clearInterval(updateIntervalId); });
    watchEffect(() => {
      if (paused.value) {
        updateCurrentTime();
        clearInterval(updateIntervalId);
      } else {
        updateIntervalId = window.setInterval(updateCurrentTime, 100);
      }
    });

    onMounted(() => {
      if (videoElement.value) videoElement.value.playbackRate = 0.25;
    });

    watchEffect(() => {

    });

    return {
      videoElement,
      paused,
      currentTime,
      keyframes: ref([]),
      updateCurrentTime,
    };
  },
  data() {
    return {
    };
  },
  computed: {
    prevKeyframe() {
      const keyframes = (this as any).keyframes as number[];
      let i = 0;
      for (;i < this.keyframes.length; i += 1) {
        const kf = keyframes[i];
        if (kf > this.currentTime) {
          return keyframes[i - 1] ?? null;
        }
      }
      return keyframes[i - 1] ?? null;
    },
    nextKeyframe() {
      const keyframes = (this as any).keyframes as number[];
      for (let i = 0; i < this.keyframes.length; i += 1) {
        const kf = keyframes[i];
        if (kf > this.currentTime) {
          return keyframes[i];
        }
      }
      return null;
    },
    keyframesWithVideo() {
      const keyframes = ((this as any).keyframes as number[]).map((kf: number) => ({ kf, isCurrent: false }));
      keyframes.push({
        kf: this.currentTime,
        isCurrent: true,
      });
      keyframes.sort((a, b) => a.kf - b.kf);
      return keyframes;
    },
  },
  methods: {
    addKeyframe() {
      const modelCopy = new Array(...this.keyframes);
      const nearestKf = Number.parseFloat(this.currentTime.toFixed(2));
      if (modelCopy.indexOf(nearestKf) === -1) {
        modelCopy.push(nearestKf);
        modelCopy.sort();
      } else {
        console.warn('Not adding keyframe - it already exists');
      }
      this.$emit('update:modelValue', modelCopy);
    },
    deleteKeyframe(timestamp: number) {
      const modelCopy = new Array(...this.keyframes);
      const index = modelCopy.indexOf(timestamp);
      // eslint-disable-next-line no-alert
      if (index !== -1 && window.confirm(`Delete keyframe at ${timestamp.toFixed(2)}?`)) {
        // const kfs = modelCopy;
        modelCopy.splice(index, 1);
        // this.keyframes = kfs;
      }

      this.$emit('update:modelValue', modelCopy);
    },
  },
});
</script>

<style lang="sass">

.keyframe-selection
  display: block

  .keyframe
    margin: 0.25rem
    // padding: 0.25rem
    border-radius: 0.25rem
    background: lightgray
    overflow: clip

    &.is-active
      background: lightblue

  .keyframe-thumb
    max-width: 200px
    max-height: 200px

</style>
