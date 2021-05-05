<template>
  <VideoPlayer
    ref="videoPlayer"
    :videoBaseUrl="videoSrc"
    @progress="onProgress"
    @playback-completed="onSegmentPlaybackCompleted"
    :videoOpacity="videoOpacity"
    :drawPoseLandmarks="drawPoseLandmarks"
    :setDrawStyle="setDrawStyle"
    :style="{
      height: '720px',
    }"
    :emphasizedJoints="emphasizedJoints"
    :emphasizedJointStyle="emphasizedJointStyle"
    />
</template>

<script lang="ts">

import { PauseInfo } from '@/model/DanceLesson';
import {
  computed, defineComponent, onBeforeUnmount, ref,
} from 'vue';
import VideoPlayer from './VideoPlayer.vue';

const DEFAULT_PAUSE_DURATION = 1.5;

type PlaySegment = {
  from: number;
  to: number;
  speed: number;
  pause: PauseInfo | null;
}
function computePlaySegments(from: number, to: number, speed: number, pauses: PauseInfo[]) {
  const segs: PlaySegment[] = [];

  function nextPauseIndex(prevIndex: number): number {
    const pTime = Math.max((pauses[prevIndex]?.time ?? 0), from);
    let pauseIndex = prevIndex + 1;
    for (; pauseIndex < pauses.length; pauseIndex += 1) {
      const pi = pauses[pauseIndex];
      if (pi.time > pTime) break;
    }
    return pauseIndex;
  }

  let segStartTime = from;
  let pauseIndex = nextPauseIndex(-1);
  while (pauseIndex < pauses.length) {
    segs.push({
      from: segStartTime,
      to: pauses[pauseIndex].time,
      speed,
      pause: pauses[pauseIndex],
    });
    segStartTime = pauses[pauseIndex].time;
    pauseIndex = nextPauseIndex(pauseIndex);
  }
  segs.push({
    from: segStartTime,
    to,
    speed,
    pause: null,
  });

  return segs;
}

export default defineComponent({
  name: 'PausingVideoPlayer',
  components: { VideoPlayer },
  props: {
    videoSrc: {
      default: '',
    },
    drawPoseLandmarks: {
      type: Boolean,
      default: false,
    },
    videoOpacity: {
      type: Number,
      default: 1,
    },
    setDrawStyle: {
      type: Function,
      default: (canvasCtx: CanvasRenderingContext2D) => {
        if (!canvasCtx) return;

        /* eslint-disable no-param-reassign */
        canvasCtx.strokeStyle = 'rgba(250, 200, 250, 0.95)';
        canvasCtx.lineWidth = 7;
        canvasCtx.lineCap = 'round';
        /* eslint-enable no-param-reassign */
      },
    },
    emphasizedJoints: {
      type: Array,
      default: Array,
    },
    emphasizedJointStyle: {
      type: String,
      default: 'red',
    },
  },
  emits: ['playback-completed', 'progress', 'pause-hit', 'pause-end'],
  setup(props, { emit }) {
    const videoPlayer = ref(null as null | typeof VideoPlayer);

    let playTimeoutId = undefined as undefined | number;

    function setTime(time: number) {
      const vidPlayer = videoPlayer.value;
      clearTimeout(playTimeoutId);
      if (vidPlayer) vidPlayer.setTime(time);
      emit('progress', time);
    }

    function onProgress(time: number) {
      emit('progress', time);
    }

    function playSegment(seg: PlaySegment, delaySecs: number, emitResume?: boolean, onPlayStart?: () => void) {
      const vidPlayer = videoPlayer.value;
      if (!vidPlayer) return;

      clearTimeout(playTimeoutId);
      playTimeoutId = setTimeout(() => {
        if (emitResume ?? false) {
          emit('pause-end');
        }
        vidPlayer.playVideo(seg.from, seg.to, seg.speed);
        if (onPlayStart) onPlayStart();
      }, 1000 * delaySecs);
    }
    onBeforeUnmount(() => {
      clearTimeout(playTimeoutId);
    });

    let playingSegments: PlaySegment[] = [];
    let playingSegmentIndex = 0;

    function play(
      from: number,
      to: number,
      speed: number,
      pauses: Array<PauseInfo>,
      playDelaySecs: number,
      onPlayStart?: () => void,
    ) {
      clearTimeout(playTimeoutId);
      setTime(from);
      playingSegments = computePlaySegments(from, to, speed, pauses);
      playingSegmentIndex = 0;

      playSegment(playingSegments[playingSegmentIndex], playDelaySecs, false, onPlayStart);
    }
    function onSegmentPlaybackCompleted() {
      const { pause, to } = playingSegments[playingSegmentIndex];
      playingSegmentIndex += 1;
      if (playingSegmentIndex >= playingSegments.length) {
        setTime(to);
        emit('playback-completed');
        return;
      }

      if (!pause) throw new Error('Expected there to be a pause obj');
      const nextSeg = playingSegments[playingSegmentIndex];

      emit('pause-hit', pause);
      const manualResume = pause.manualResume ?? false;
      if (!manualResume) {
        playSegment(nextSeg, pause.pauseDuration ?? DEFAULT_PAUSE_DURATION, true);
      }
    }

    const currentPose = computed(() => videoPlayer.value?.currentPose ?? null);

    return {
      videoPlayer,
      setTime,
      onProgress,
      onSegmentPlaybackCompleted,
      play,
      currentPose,
    };
  },
  methods: {
    getVideoDimensions() {
      return (this.$refs.videoPlayer as typeof VideoPlayer)?.getVideoDimensions();
    },
  },
});
</script>

<style>

</style>
