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
      <MainMenuWorkflowCard
        v-for="workflow in whitelistedWorkflows"
        :workflow="workflow"
        :key="workflow.id"
        @click="$emit('workflow-selected', workflow.id)"
      ></MainMenuWorkflowCard>
    </div>
    <div class="is-justify-content-center is-flex" v-if="nonwhitelistedWorkflows.length > 0 && currentTab === Tabs.Workflows">
      <button class="button is-ghost" @click="() => isWorkflowListExpanded = !isWorkflowListExpanded">
        <span v-if="isWorkflowListExpanded">
          <i class="fas fa-minus"></i>
          Show Less
        </span>
        <span v-else>
          <i class="fas fa-plus"></i>
          Show All
        </span>
      </button>
    </div>
    <div class="grid-menu container block" v-if="nonwhitelistedWorkflows.length > 0 && currentTab === Tabs.Workflows && isWorkflowListExpanded">
      <MainMenuWorkflowCard
        v-for="workflow in nonwhitelistedWorkflows"
        :workflow="workflow"
        :key="workflow.id"
        @click="$emit('workflow-selected', workflow.id)"
      ></MainMenuWorkflowCard>
    </div>

    <div v-if="currentTab === Tabs.Videos && availableTags.size > 0" class="has-text-centered container">
      <!-- <h3 class="subtitle">Tags</h3> -->
      <strong>Filter by tag: </strong>
      <span
        v-for="tag in availableTags"
        :key="tag"
        class="tag m-1 is-size-6 is-clickable is-unselectable"
        :class="{'is-primary': activeTags.has(tag)}"
        @click="toggleTag(tag)"
      >{{tag}}</span>

    </div>

    <div class="grid-menu container block"
      v-show="currentTab === Tabs.Videos"
    >
      <div
        class="video-card card hover-expand"
        v-for="videoEntry in filteredVideos"
        :key="videoEntry.clipName"
        @mouseover="videoEntry.hovering = true"
        @mouseleave="videoEntry.hovering = false"
        @click = "videoEntry.clicked = !videoEntry.clicked"
      >
        <div class="card-image">
          <figure class="image is-2by3" v-if="(!videoEntry.hovering) && (!videoEntry.clicked)">
            <img :src="videoEntry.thumbnailSrc" class="is-contain" />
          </figure>
          <figure class="image is-2by3" v-else><video controls :src="videoEntry.videoSrc" @playing="videoEntry.clicked=True"></video></figure>
        </div>
        <div class="card-content" >
          <div class="level">
            <div class="level-item">
              {{ videoEntry.title }}
            </div>
            <!-- <transition name="expand-down" appear> -->
              <div class="level-item">
                <button
                  class="button is-small transition-all is-primary"
                  :class="{
                    'is-outlined': !(videoEntry.clicked || videoEntry.hovering)
                  }"
                  @click="selectedVideo = videoEntry">
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
      <div class="box hover-expand is-clickable m-4" @click="$emit('create-workflow-selected')">
        Workflow Editor
      </div>
    </div>

    <div v-bind:class="{ 'is-active': selectedVideo }" class="modal">
      <div class="modal-background"></div>
      <div class="modal-content">
        <LessonCard
          :motion="selectedVideo"
          @closed="selectedVideo = null"
          @lesson-selected="onLessonSelected"
          @create-lesson-selected="createLessonSelected"
          @keyframeselectortool-selected="onKeyframeSelectorToolSelected"
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
import MainMenuWorkflowCard from '@/components/elements/MainMenuWorkflowCard.vue';
import LessonCard from '@/components/elements/LessonCard.vue';
import UploadCard from '@/components/elements/UploadCard.vue';
import VideoDatabaseEntry from '@/model/VideoDatabaseEntry';
import miniLessonManager, { MiniLessonManager } from '@/services/MiniLessonManager';
import db from '@/services/VideoDatabase';
import MiniLesson from '@/model/MiniLesson';
import workflowManager, { WorkflowManager } from '@/services/WorkflowManager';
import optionsManager from '@/services/OptionsManager';

const workflowWhitelist = [
  'c8829142-992b-4cda-8ef7-ff0813f6e6fb',
  '15752163-7086-4305-a7be-39affe5c7e57',
];

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
    'create-lesson-selected',
    'workflow-selected',
    'create-workflow-selected',
    'keyframeselectortool-selected',
  ],
  components: {
    LessonCard,
    UploadCard,
    MainMenuWorkflowCard,
  },
  setup(props, ctx) {
    const videos = db.entries;
    const selectedVideo = ref(null as VideoDatabaseEntry | null);
    const uploadLessonUIActive = ref(false);
    const currentTab = ref(Tabs.Workflows as string);
    const activeTags = ref(new Set());

    function onLessonSelected(
      videoEntry: VideoDatabaseEntry,
      lesson: MiniLesson,
    ) {
      ctx.emit('lesson-selected', videoEntry, lesson);
      selectedVideo.value = null;
    }

    function createLessonSelected(videoEntry: VideoDatabaseEntry) {
      ctx.emit('create-lesson-selected', videoEntry);
      selectedVideo.value = null;
    }

    const filteredVideos = computed(() => {
      const tagMatchingMotions = videos.value.filter((videoEntry) => {

        if (activeTags.value.size === 0) return true;

        const allTagsMatch = videoEntry.tags.reduce((someTagMatches: boolean, currTag: string) => {
          const thisTagMatches = activeTags.value.has(currTag);
          return someTagMatches || thisTagMatches;
        }, false);

        return allTagsMatch;

      });

      return tagMatchingMotions;
    });

    // eslint-disable-next-line arrow-body-style
    const whitelistedWorkflows = computed(() => {
      // eslint-disable-next-line arrow-body-style
      return workflowManager.workflowsArray.value.filter((workflow) => {
        return workflowWhitelist.length === 0 || workflowWhitelist.includes(workflow.id);
      });
    });

    // eslint-disable-next-line arrow-body-style
    const nonwhitelistedWorkflows = computed(() => {
      // eslint-disable-next-line arrow-body-style
      return workflowManager.workflowsArray.value.filter((workflow) => {
        return workflowWhitelist.length === 0 || !workflowWhitelist.includes(workflow.id);
      });
    });

    return {
      whitelistedWorkflows,
      nonwhitelistedWorkflows,
      isDebug: optionsManager.isDebug,
      isWorkflowListExpanded: ref(false),
      selectedVideo,
      videos,
      filteredVideos,
      onLessonSelected,
      createLessonSelected,
      uploadLessonUIActive,
      uploadWorkflowUIActive: ref(false),
      workflowManager,
      activeTags,
      availableTags: db.allTags,
      TabList,
      Tabs,
      currentTab,
    };
  },
  methods: {
    toggleTag(tag: string) {
      if (this.activeTags.has(tag)) {
        this.activeTags.delete(tag);
      } else {
        this.activeTags.add(tag);
      }
    },
    setTab(tab: string) {
      console.log('Switching to tab:', tab);
      if (!TabSet.has(tab)) {
        console.error(`Tab ${tab} not recognized!`);
        return;
      }
      this.currentTab = tab;
    },
    onKeyframeSelectorToolSelected(videoEntry: VideoDatabaseEntry, keyframes: number[]) {
      this.$emit('keyframeselectortool-selected', videoEntry, keyframes);
    },
    async uploadLessons(files: FileList) {
      console.log('Uploading lessons', files);

      for (let i = 0; i < files.length; i += 1) {
        const file = files.item(i);
        if (!file) continue;
        // eslint-disable-next-line no-await-in-loop
        const text = await file.text();
        const lesson = JSON.parse(text);
        MiniLessonManager.validateLesson(lesson);
        miniLessonManager.saveCustomLesson(lesson);
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

.video-card.card {
  max-width: 300px;
}

.video-card {
  width: 210px;
  flex-grow: 1;

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
