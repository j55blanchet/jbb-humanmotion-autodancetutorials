<template>
<!-- <div class="test123">
  <div class="flexpar">
    <div class="flexexpand"></div>
    <div class="flexbar"></div>
  </div>
</div> -->
  <div class="layout-test">
    <MiniLessonPlayer
      :videoEntry="{
        videoSrc: 'videos/derulo.mp4',
      }"
      :miniLesson="miniLesson"
      :drawPoseLandmarks="true"
    />
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import MiniLessonPlayer from '@/components/elements/MiniLessonPlayer.vue';
import MiniLesson from '@/model/MiniLesson';

const miniLesson: MiniLesson = {
  _id: 'f60a2a6c-6324-4cb0-8034-38f3ac077a17',
  header: {
    clipName: 'renegade',
    lessonTitle: '65% Practice',
  },
  segmentBreaks: [
    0,
    2.3333333333333335,
    7.7,
    12.233333333333333,
  ],
  activities: [
    {
      title: 'Refresher',
      startTime: 0,
      endTime: 12.233333333333333,
      demoVisual: 'video',
      userVisual: 'none',
      focusedSegments: [
        0,
        1,
        2,
      ],
      pauses: [],
      practiceSpeed: 0.5,
      startInstruction: "We're going to speed it up a bit now",
      timedInstructions: [],
      endInstruction: "Next you'll try it at this speed WITHOUT the video!",
      playingInstruction: 'Follow along',
    },
    {
      title: 'No Video',
      startTime: 0,
      endTime: 12.233333333333333,
      demoVisual: 'skeleton',
      userVisual: 'video',
      focusedSegments: [
        0,
        1,
        2,
      ],
      pauses: [],
      startInstruction: 'Follow along with the teacher skeleton!',
      timedInstructions: [],
      practiceSpeed: 0.65,
      endInstruction: "Repeat until you've got it!",
      playingInstruction: '',
    },
  ],
  source: 'builtin',
};

export default defineComponent({
  components: {
    MiniLessonPlayer,
  },
  data() {
    return {
      miniLesson,
    };
  },
});
</script>

<style lang="scss">
.layout-test {
  background: white;
  padding: 1rem;
  // margin: 0 auto;

  width: 100vw;
  height: calc(100vh);

  // overflow: hidden;
  box-sizing: border-box;
  // height: 400px;
}

.test123 {
  margin: 0 auto;
  width: 300px;
  height: 300px;
  padding: 50px;
  background: black;

  .flexpar {
    display: flex;
    flex-flow: column nowrap;
    height: 100%;
    width: 100%;
    background: gray;
  }

  .flexbar {
    flex: 0 0 auto;
    height: 150px;
    background: green;
  }

  .flexexpand {
    flex: 1 1 0;
    background: blue;
    height: 200px;
  }
}
</style>
