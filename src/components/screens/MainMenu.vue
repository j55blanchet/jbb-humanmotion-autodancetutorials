<template>
  <section class="section dance-menu">

    <div class="hero is-primary block">
      <div class="hero-body">
        <div class="container">
          <p class="title">
            Main Menu
          </p>
          <p class="subtitle mb-0">
            What do you want to learn?
          </p>
        </div>
      </div>
    </div>

    <div class="tabs is-centered is-medium is-toggle is-toggle-rounded">
      <ul>
        <li v-for="(tab, i) in TabList" :key="i" :class="{'is-active': currentTab===tab}">
          <a @click="setTab(tab)">{{tab}}</a>
        </li>
      </ul>
    </div>

    <div class="menu container block" v-show="currentTab === Tabs.Workflows">
      <div class="box m-0 hover-expand is-clickable"
        v-for="workflow in workflows"
        :key="workflow.id"
        @click="$emit('workflow-selected', workflow.id)">{{workflow.title}}
      </div>
    </div>

    <div class="grid-menu container block"
      v-show="currentTab === Tabs.Videos"
    >
      <div
        class="dance-card card hover-expand"
        v-for="dance in motionList"
        :key="dance.title"
        @mouseover="hover = dance.hovering = true"
        @mouseleave="hover = dance.hovering = false"
      >
        <div class="card-image">
          <figure class="image is-2by3" v-if="!dance.hovering">
            <img :src="dance.thumbnailSrc" class="is-contain" />
          </figure>
          <figure class="image is-2by3" v-else><video controls :src="dance.videoSrc" ></video></figure>
        </div>
        <div class="card-content" >
          <div class="level">
            <div class="level-item">
              {{ dance.title }}
            </div>
            <div class="level-item" v-show="dance.hovering">
              <button class="button is-primary" @click="selectedDance = dance">Go!</button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="grid-menu container block" v-show="currentTab === Tabs.Tools">
      <div class="box hover-expand is-clickable m-0" @click="uploadUIActive = true">
        Upload Custom Lesson
      </div>
      <div class="box hover-expand is-clickable m-0" @click="$emit('pose-drawer-selected')">
        Pose Drawer Test
      </div>
    </div>

    <div v-bind:class="{ 'is-active': selectedDance }" class="modal">
      <div class="modal-background"></div>
      <div class="modal-content">
        <LessonCard
          :motion="selectedDance"
          @closed="selectedDance = null"
          @lesson-selected="videoLessonSelected"
          @create-lesson-selected="createLessonSelected"
        />
      </div>
    </div>

    <div v-bind:class="{ 'is-active': uploadUIActive }" class="modal">
      <div class="modal-background"></div>
      <div class="modal-content">
        <UploadCard
          v-if="uploadUIActive"
          @cancelled="uploadUIActive = false"
          :uploadAccept="'*.json'"
          :onFilesSelected="uploadFiles"
          :savingText="'Loading lessons...'"
          :successText="'Lessons loaded successfully'"
        />
      </div>
    </div>
  </section>
</template>

<script lang="ts">
import { computed, defineComponent, ref } from 'vue';
import LessonCard from '@/components/elements/LessonCard.vue';
import UploadCard from '@/components/elements/UploadCard.vue';
import db, { DatabaseEntry } from '@/services/MotionDatabase';
import VideoLesson from '@/model/VideoLesson';
import workflowManager from '@/services/WorkflowManager';

const Tabs = Object.freeze({
  Workflows: 'Workflows',
  Videos: 'Videos',
  Tools: 'Tools',
});
const TabSet = Object.freeze(new Set(Object.values(Tabs)));
const TabList = Object.freeze(new Array(...Object.values(Tabs)));

export default defineComponent({
  name: 'MainMenu',
  emits: [
    'video-selected',
    'pose-drawer-selected',
    'create-lesson-selected',
    'workflow-selected',
  ],
  components: {
    LessonCard,
    UploadCard,
  },
  setup(props, ctx) {
    const motionList = db.motions;
    const selectedDance = ref(null as DatabaseEntry | null);
    const uploadUIActive = ref(false);
    const currentTab = ref(Tabs.Workflows);

    function videoLessonSelected(
      videoEntry: DatabaseEntry,
      lesson: VideoLesson,
    ) {
      ctx.emit('video-selected', videoEntry, lesson);
      selectedDance.value = null;
    }

    function createLessonSelected(videoEntry: DatabaseEntry) {
      ctx.emit('create-lesson-selected', videoEntry);
      selectedDance.value = null;
    }

    return {
      workflows: workflowManager.allWorkflows,
      selectedDance,
      motionList,
      videoLessonSelected,
      createLessonSelected,
      uploadUIActive,
      workflowManager,

      TabList,
      Tabs,
      currentTab,
    };
  },
  methods: {
    setTab(tab: string) {
      console.log('Switching to tab:', tab);
      if (!TabSet.has(tab)) {
        console.error(`Tab ${tab} not recognized!`);
        return;
      }
      this.currentTab = tab;
    },
    async uploadFiles(files: FileList) {
      console.log('Upload files', files);

      for (let i = 0; i < files.length; i += 1) {
        const file = files.item(i);
        if (!file) continue;
        // eslint-disable-next-line no-await-in-loop
        const text = await file.text();
        const lesson = JSON.parse(text);
        db.validateLesson(lesson);

        // TODO: validate lesson
        db.saveCustomLesson(lesson);
      }
      return true;
    },
  },
});
</script>

<style lang="scss">
// .dance-menu {
// backdrop-filter: blur(4px);
// background: rgba(0, 0, 0, 0.2);
// }

.dance-menu {
  .menu .card {
    display: block;
  }
  .dance-card {
    height: max-content;
    overflow: hidden;
    // transition: transform 0.2s, box-shadow 0.2s;

    // &:hover {
    //   box-shadow: 0 0.5em 1em -0.125em rgba(10, 10, 10, 0.3),
    //     0 0 0 2px rgba(10, 10, 10, 0.05);
    //   transform: scale(0.98);
    // }
  }

  img {
    object-fit: cover;
  }

  .subtitle {
    margin: 2rem 1rem 2em;
    color: white;
  }

  .section {
    padding: 1.5rem;
  }

  .image video {
    bottom: 0;
    left: 0;
    right: 0;
    top: 0;
    position: absolute;
    width: 100%;
    height: 100%;
    object-fit: cover;
  }
}
</style>
