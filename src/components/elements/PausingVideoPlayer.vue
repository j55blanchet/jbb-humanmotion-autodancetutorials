<template>
  <VideoPlayer
    :height="'720px'"
    ref="videoPlayer"
    :videoBaseUrl="videoSrc"
    @progress="onProgress"
    @playback-completed="onSegmentPlaybackCompleted"
    />
</template>

<script lang="ts">

import { PauseInfo } from '@/model/DanceLesson';
import { defineComponent, ref } from 'vue';
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
  },
  emits: ['playback-completed', 'progress', 'pause-hit', 'pause-end'],
  setup(props, { emit }) {
    const videoPlayer = ref(null as null | typeof VideoPlayer);

    function setTime(time: number) {
      const vidPlayer = videoPlayer.value;
      if (vidPlayer) vidPlayer.setTime(time);
      emit('progress', time);
    }

    function onProgress(time: number) {
      emit('progress', time);
    }

    function playSegment(seg: PlaySegment, delaySecs: number, emitResume?: boolean) {
      const vidPlayer = videoPlayer.value;
      if (!vidPlayer) return;

      vidPlayer.setTime(seg.from);
      setTimeout(() => {
        if (emitResume) {
          emit('pause-end');
        }
        vidPlayer.playVideo(seg.from, seg.to, seg.speed);
      }, 1000 * delaySecs);
    }

    let playingSegments: PlaySegment[] = [];
    let playingSegmentIndex = 0;

    function play(
      from: number,
      to: number,
      speed: number,
      pauses: Array<PauseInfo>,
      playDelaySecs: number,
    ) {
      setTime(from);
      playingSegments = computePlaySegments(from, to, speed, pauses);
      playingSegmentIndex = 0;

      playSegment(playingSegments[playingSegmentIndex], playDelaySecs);
    }
    function onSegmentPlaybackCompleted() {
      const { pause } = playingSegments[playingSegmentIndex];
      playingSegmentIndex += 1;
      if (playingSegmentIndex >= playingSegments.length) {
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

    return {
      videoPlayer,
      setTime,
      onProgress,
      onSegmentPlaybackCompleted,
      play,
    };
  },
});
</script>

<style>

</style>
