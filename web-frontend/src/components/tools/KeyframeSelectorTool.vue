<template>
  <section class="keyframe-selection section">
    <div class="container box">
      <h1 class="title">Keyframe Selection Tool</h1>

      <div class="buttons">
        <button class="button" @click="$emit('back-selected')">Done</button>
      </div>

      <div class="block has-text-centered">
        <video
          ref="videoElement"
          @playing="paused = false"
          @pause="paused = true"
          @seeked="updateCurrentTime"
          :src="videoEntry.videoSrc"
          controls
          style="max-height: 50vh; max-width: 768px;margin:auto;"></video>
      </div>

      <div class="buttons is-grouped is-centered">
        <button class="button" @click="videoElement.currentTime -= 0.1">&lt;&lt;</button>
        <button class="button" @click="videoElement.currentTime -= 0.03">&lt;</button>
        <span class="button is-text" disabled>
          {{currentTime.toFixed(2)}}s
        </span>
        <button class="button" @click="addKeyframe">&plus; Add</button>
        <button class="button" @click="videoElement.currentTime += 0.03">&gt;</button>
        <button class="button" @click="videoElement.currentTime += 0.1">&gt;&gt;</button>
      </div>
      <div>
        <input class="slider is-fullwidth" type="range" :value="currentTime" :min="videoEntry.startTime" :max="videoEntry.endTime" step="0.03" @input="this.$refs.videoElement.currentTime = $event.target.value">
      </div>
      <div class="field is-horizontal">
        <div class="field-label">
          <label class="label">Draw Mode</label>
        </div>
        <div class="field-body">
          <div class="field">
            <div class="control">
              <div class="select">
                <select v-model="drawMode">
                  <!-- <option value="none">None</option> -->
                  <option value="skeleton">Skeleton</option>
                  <option value="video">Video</option>
                </select>
              </div>
            </div>
          </div>
        </div>
      </div>
<!--
      <div class="block">
        <pre>{{JSON.stringify(modelValue)}}</pre>
      </div> -->

      <div class="block">
        <KeyframeTimeline
          :keyframes="modelValue"
          :currentTime="currentTime"
          :dbEntry="videoEntry"
          :showTimestamps="true"
          :drawMode="drawMode"
        />
      </div>

      <div class="block">
        <h3 class="subtitle">Keyframes</h3>
        <div class="is-flex is-flex-wrap-wrap">
          <div class="keyframe">
            <div class="vcenter-parent">
              <div class="p-1 has-text-centered">
                StartTime<br />
                <span class="tag">{{effectiveStartTime.toFixed(2)}}s</span>
              </div>
            </div>
          </div>
          <div
              class="keyframe is-relative  over-expand is-clickable"
              v-for="kf in modelValue"
              :key="kf"
              @click="deleteKeyframe(kf)">

            <!-- <div class="has-text-right is-overlay"><button class="button is-small is-danger is-light">&times;</button></div> -->
            <video class="keyframe-thumb"
            :src="videoEntry.videoSrc + '#t=' + kf">
            </video>
            <div class="has-text-centered mb-2"><span class="tag">{{kf.toFixed(2)}}</span></div>
          </div>
          <div class="keyframe">
            <div class="vcenter-parent">
              <div class="p-1 has-text-centered">
                EndTime<br />
                <span class="tag">{{effectiveEndTime.toFixed(2)}}s</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script lang="ts">
import {
  computed,
  defineComponent, onBeforeUnmount, onMounted, ref, toRefs, watchEffect,
} from 'vue';
import KeyframeTimeline from '@/components/elements/KeyframeTimeline.vue';
// import videoDBVideoDatabaseEntry } from '@/services/VideoDatabase';

// [2.28,2.73,2.93,3.18,3.26,3.47,3.54,3.69,4.02,4.2,4.35,4.53,4.71,4.98,5.13,5.44,5.53]
export default defineComponent({
  name: 'KeyframeSelectorTool',
  emits: ['back-selected', 'update:modelValue'],
  components: {
    KeyframeTimeline,
  },
  props: {
    videoEntry: {
      type: Object,
      required: true,
    },
    modelValue: {
      type: Array,
      default: Array,
      required: true,
    },
    startTime: {
      type: Number,
      default: -1,
    },
    endTime: {
      type: Number,
      default: -1,
    },
  },
  setup(props) {
    const {
      modelValue, startTime, endTime, videoEntry,
    } = toRefs(props);
    const paused = ref(false);
    const currentTime = ref(0);
    const videoElement = ref(null as HTMLVideoElement | null);

    const effectiveStartTime = computed(() => {
      if (startTime.value > 0) return startTime.value;
      if (videoEntry.value?.startTime) return videoEntry.value.startTime;
      return 0;
    });
    const effectiveEndTime = computed(() => {
      if (endTime.value > 0) return endTime.value;
      if (videoEntry.value?.endTime) return videoEntry.value.endTime;
      if (videoEntry.value?.duration) return videoEntry.value.duration;
      return -1;
    });

    onMounted(() => {
      if (videoElement.value) videoElement.value.currentTime = effectiveStartTime.value;
    });

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
      updateCurrentTime,
      drawMode: ref('skeleton'),

      effectiveStartTime,
      effectiveEndTime,
    };
  },
  data() {
    return {
    };
  },
  computed: {
    prevKeyframe() {
      const keyframes = (this as any).modelValue as number[];
      let i = 0;
      for (;i < this.modelValue.length; i += 1) {
        const kf = keyframes[i];
        if (kf > this.currentTime) {
          return keyframes[i - 1] ?? null;
        }
      }
      return keyframes[i - 1] ?? null;
    },
    nextKeyframe() {
      const keyframes = (this as any).modelValue as number[];
      for (let i = 0; i < this.modelValue.length; i += 1) {
        const kf = keyframes[i];
        if (kf > this.currentTime) {
          return keyframes[i];
        }
      }
      return null;
    },
  },
  methods: {
    addKeyframe() {
      const modelCopy = [...this.modelValue];
      const nearestKf = Number.parseFloat(this.currentTime.toFixed(2));
      if (modelCopy.indexOf(nearestKf) === -1) {
        modelCopy.push(nearestKf);
        modelCopy.sort();
      } else {
        console.warn('Not adding keyframe - it already exists');
      }
      this.$emit('update:modelValue', modelCopy);
      console.log('update:modelValue (added kf)', modelCopy);
    },
    deleteKeyframe(timestamp: number) {
      const modelCopy = [...this.modelValue];
      const index = modelCopy.indexOf(timestamp);
      // eslint-disable-next-line no-alert
      if (index !== -1 && window.confirm(`Delete keyframe at ${timestamp.toFixed(2)}?`)) {
        // const kfs = modelCopy;
        modelCopy.splice(index, 1);
        // this.keyframes = kfs;
      }

      this.$emit('update:modelValue', modelCopy);
      console.log('update:modelValue (deleted kf)', modelCopy);
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
