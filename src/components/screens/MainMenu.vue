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

    <div class="tabs is-centered is-medium-desktop is-small-mobile is-toggle is-toggle-rounded">
      <ul>
        <li v-for="(tab, i) in TabList" :key="i" :class="{'is-active': currentTab===tab}">
          <a @click="setTab(tab)">{{tab}}</a>
        </li>
      </ul>
    </div>

    <div class="grid-menu container block" v-show="currentTab === Tabs.Workflows">
      <div class="box m-4 hover-expand is-clickable"
        v-for="workflow in workflows"
        :key="workflow.id"
        @click="$emit('workflow-selected', workflow.id)">{{workflow.title}}
      </div>
    </div>

    <div class="grid-menu container block"
      v-show="currentTab === Tabs.Videos"
    >
      <div
        class="video-card card hover-expand"
        v-for="dance in motionList"
        :key="dance.title"
        @mouseover="dance.hovering = true"
        @mouseleave="dance.hovering = false"
        @click = "dance.clicked = !dance.clicked"
      >
        <div class="card-image">
          <figure class="image is-2by3" v-if="(!dance.hovering) && (!dance.clicked)">
            <img :src="dance.thumbnailSrc" class="is-contain" />
          </figure>
          <figure class="image is-2by3" v-else><video controls :src="dance.videoSrc" @playing="dance.clicked=True"></video></figure>
        </div>
        <div class="card-content" >
          <div class="level">
            <div class="level-item">
              {{ dance.title }}
            </div>
            <!-- <transition name="expand-down" appear> -->
              <div class="level-item">
                <button
                  class="button is-small transition-all is-primary"
                  :class="{
                    'is-outlined': !(dance.clicked || dance.hovering)
                  }"
                  @click="selectedDance = dance">
                  <span>Go</span>
                  <span class="icon is-small">
                    <i class="fas fa-arrow-right"></i>
                  </span>
                  </button>
              </div>
            <!-- </transition> -->
          </div>
        </div>
      </div>
    </div>

    <div class="grid-menu container block" v-show="currentTab === Tabs.Tools">
      <div class="box hover-expand is-clickable m-4" @click="uploadLessonUIActive = true">
        Upload Custom Lesson
      </div>
      <div class="box hover-expand is-clickable m-4" @click="uploadWorkflowUIActive = true">
        Upload Custom Workflow
      </div>
      <div class="box hover-expand is-clickable m-4" @click="$emit('pose-drawer-selected')">
        Pose Drawer Test
      </div>
      <div class="box hover-expand is-clickable m-4" @click="$emit('create-workflow-selected')">
        Workflow Editor
      </div>
    </div>

    <div v-bind:class="{ 'is-active': selectedDance }" class="modal">
      <div class="modal-background"></div>
      <div class="modal-content">
        <LessonCard
          :motion="selectedDance"
          @closed="selectedDance = null"
          @lesson-selected="onLessonSelected"
          @create-lesson-selected="createLessonSelected"
        />
      </div>
    </div>

    <div v-bind:class="{ 'is-active': uploadLessonUIActive }" class="modal">
      <div class="modal-background"></div>
      <div class="modal-content">
        <UploadCard
          v-if="uploadLessonUIActive"
          @cancelled="uploadLessonUIActive = false"
          :uploadAccept="'*.json'"
          :onFilesSelected="uploadLessons"
          :savingText="'Loading lessons...'"
          :successText="'Lessons loaded successfully'"
        />
      </div>
    </div>

    <div v-bind:class="{ 'is-active': uploadWorkflowUIActive }" class="modal">
      <div class="modal-background"></div>
      <div class="modal-content">
        <UploadCard
          v-if="uploadWorkflowUIActive"
          @cancelled="uploadWorkflowUIActive = false"
          :uploadAccept="'*.json'"
          :onFilesSelected="uploadWorkflows"
          :savingText="'Loading workflows...'"
          :successText="'Workflows loaded successfully'"
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
import VideoLesson from '@/model/MiniLesson';
import workflowManager, { WorkflowManager } from '@/services/WorkflowManager';

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
    'lesson-selected',
    'pose-drawer-selected',
    'create-lesson-selected',
    'workflow-selected',
    'create-workflow-selected',
  ],
  components: {
    LessonCard,
    UploadCard,
  },
  setup(props, ctx) {
    const motionList = db.motions;
    const selectedDance = ref(null as DatabaseEntry | null);
    const uploadLessonUIActive = ref(false);
    const currentTab = ref(Tabs.Tools);

    function onLessonSelected(
      videoEntry: DatabaseEntry,
      lesson: VideoLesson,
    ) {
      ctx.emit('lesson-selected', videoEntry, lesson);
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
      onLessonSelected,
      createLessonSelected,
      uploadLessonUIActive,
      uploadWorkflowUIActive: ref(false),
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
    async uploadLessons(files: FileList) {
      console.log('Uploading lessons', files);

      for (let i = 0; i < files.length; i += 1) {
        const file = files.item(i);
        if (!file) continue;
        // eslint-disable-next-line no-await-in-loop
        const text = await file.text();
        const lesson = JSON.parse(text);
        db.validateLesson(lesson);
        db.saveCustomLesson(lesson);
      }
      return true;
    },
    async uploadWorkflows(files: FileList) {
      console.log('Uploading workflows', files);

      for (let i = 0; i < files.length; i += 1) {
        const file = files.item(i);
        if (!file) continue;
        // eslint-disable-next-line no-await-in-loop
        const text = await file.text();
        const workflow = JSON.parse(text);
        WorkflowManager.validateWorkflow(workflow);

        if (workflowManager.hasBakedInWorkflow(workflow.id)) throw new Error(`Cannot overwrite baked in workflow ${workflowManager.workflows.get(workflow.id)?.title}`);

        // eslint-disable-next-line no-alert
        if (!workflowManager.hasWorkflow(workflow.id) || window.confirm(`Are you sure you want to overwrite workflow '${workflowManager.workflows.get(workflow.id)?.title}'?`)) {
          workflowManager.upsertCustomWorkflow(workflow);
        }
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

.video-card {
  width: 210px;
  flex-grow: 1;
  max-width: 300px;
  margin: 1em;

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

/* Enter and leave animations can use different */
/* durations and timing functions.              */
.expand-down-enter-active {
  transition: all .3s ease;
}
.expand-down-leave-active {
  transition: all .8s cubic-bezier(1.0, 0.5, 0.8, 1.0);
}
.expand-down-enter, .expand-down-leave-to
/* .slide-fade-leave-active below version 2.1.8 */ {
  transform: scaleY(0);
  height: 0;
  opacity: 0;
}
.collapsed {
  transform: scaleY(0);
  height: 0;
}
.animate-height {
  transition: transform 0.15s ease;
}

.transition-all {
  transition: all 0.15s ease;
}
</style>
