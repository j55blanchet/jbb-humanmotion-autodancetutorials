<template>
    <teleport to="#topbarLeft">

    </teleport>

    <section class="section">
      <div class="hero is-primary block">
        <div class="hero-body">
          <div class="container">
            <p class="title">
              Lesson Creation
            </p>
            <p class="subtitle">
              {{state}}
            </p>
          </div>
        </div>
      </div>

      <div class="container block"><button class="button" @click="$emit('back-selected')">&lt; Back</button></div>

      <div v-if="state === LessonCreationState.SelectOpenLesson" class="container has-text-centered">
        <div class="card block center-block has-text-left">
          <div class="card-header">
            <h4 class="card-header-title">Pick a template:</h4>
          </div>
          <div class="card-content menu">
            <ul class="menu-list">
              <li><a @click="startCreation(null)">(start from scratch)</a></li>
              <li v-for="lesson in lessons" :key="lesson._id"><a @click="startCreation(lesson)">{{lesson.header.lessonTitle}}</a></li>
            </ul>
          </div>
        </div>
      </div>

      <div v-if="state === LessonCreationState.ModifyLesson" class="container block">
        <div class="columns">
          <div class="column is-narrow">

            <h5 class="title is-5">Lesson</h5>

            <div class="field is-horizontal">
              <div class="field-label is-normal">
                <label class="label">Clip</label>
              </div>
              <div class="field-body">
                <div class="field">
                  <div class="control">
                    <input class="input" disabled type="text" :value="motion.title">
                  </div>
                </div>
              </div>
            </div>

            <div class="field is-horizontal">
              <div class="field-label is-normal">
                <label class="label">Title</label>
              </div>
              <div class="field-body">
                <div class="field">
                  <div class="control">
                    <input class="input" type="text" v-model="lessonUnderConstruction.header.lessonTitle">
                  </div>
                </div>
              </div>
            </div>

            <div class="field is-horizontal">
              <div class="field-label">
                <label class="label">Activities</label>
              </div>
              <div class="field-body">
                <div class="field">
                  <div class="control">
                    <ul class="menu-list">
                      <li v-for="(activity, i) in lessonUnderConstruction.activities" :key="i">
                        <a :class="{'is-active': activeActivityIndex === i}" @click="selectActivity(i)"><strong>{{i+1}}&nbsp;</strong>&nbsp;{{activity.title}}</a>
                      </li>
                      <li><a @click="addActivity()">&plus; Add Activity</a></li>
                      <li v-if="lessonUnderConstruction.activities.length === 0">No Activities</li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="column is-narrow">

            <h5 class="title is-5">Activity</h5>

            <div class="field is-horizontal">
              <div class="field-label">
                <label class="label">Title</label>
              </div>
              <div class="field-body">
                <div class="field">
                  <div class="control">
                    <input type="text" class="input" v-model="activeActivity.title" />
                  </div>
                </div>
              </div>
            </div>

            <div class="field is-horizontal">
              <div class="field-label">
                <label class="label">Start Time</label>
              </div>
              <div class="field-body">
                <div class="field">
                  <div class="control">
                    <input type="text" class="input" v-model="activeActivity.startTime">
                  </div>
                </div>
                <div class="field">
                  <div class="control">
                    <input type="range" class="input slider mt-0 mb-0" v-model="activeActivity.startTime" min="0" step="0.1" :max="activeActivity.endTime"/>
                  </div>
                </div>
              </div>
            </div>

            <div class="field is-horizontal">
              <div class="field-label">
                <label class="label">End Time</label>
              </div>
              <div class="field-body">
                <div class="field">
                  <div class="control">
                    <input type="text" class="input" v-model="activeActivity.endTime">
                  </div>
                </div>
                <div class="field">
                  <div class="control">
                    <input type="range" class="input slider mt-0 mb-0" v-model="activeActivity.endTime" :min="activeActivity.startTime" step="0.1" :max="motion.duration"/>
                  </div>
                </div>
              </div>
            </div>
            <!-- <div class="field is-horizontal">
              <div class="field-label"></div>
              <div class="field-body">
                <div class="field">
                  <div class="control">
                    <input type="range" class="input slider" v-model="activeActivity.startTime" min="0" step="0.1" :max="motion.duration"/>
                  </div>
                </div>
              </div>
            </div> -->

          </div>

          <div class="column">

            <h5 class="title is-5">Demo</h5>
          </div>
        </div>
      </div>

    </section>

    <teleport to='#belowSurface'>
    </teleport>
</template>

<script lang="ts">

import {
  computed,
  defineComponent, ref, toRefs,
} from 'vue';

// import VideoPlayer from '@/components/elements/VideoPlayer.vue';
import db, { createBlankLesson, DatabaseEntry } from '@/services/MotionDatabase';
import DanceLesson, { Activity } from '@/model/DanceLesson';
import Utils from '@/services/Utils';

const LessonCreationState = Object.freeze({
  SelectOpenLesson: 'SelectOpenLesson',
  ModifyLesson: 'ModifyLesson',
});

export default defineComponent({
  name: 'CreateLessonScreen',
  components: {
    // VideoPlayer,
  },
  props: ['motion'],
  emits: ['back-selected', 'lesson-created'],
  computed: {
    lessons() {
      if (!this.motion) return [];
      const motion = this.motion as DatabaseEntry;
      const lessons = db.getLessons(motion);
      return lessons ?? [];
    },
  },
  setup(props) {
    const { motion } = toRefs(props);
    const typedMotion = computed(() => motion.value as unknown as DatabaseEntry);
    const state = ref(LessonCreationState.SelectOpenLesson);
    const lessonUnderConstruction = ref(createBlankLesson(motion));
    const activeActivityIndex = ref(0);
    const activeActivity = computed(() => lessonUnderConstruction.value.activities[activeActivityIndex.value]);
    return {
      state,
      typedMotion,
      LessonCreationState,
      lessonUnderConstruction,
      activeActivityIndex,
      activeActivity,
    };
  },
  methods: {
    startCreation(lesson: DanceLesson | null) {
      if (lesson) {
        this.lessonUnderConstruction = Utils.deepCopy(lesson);
        // eslint-disable-next-line no-underscore-dangle
        this.lessonUnderConstruction._id = Utils.uuidv4();

      } else {
        this.lessonUnderConstruction = createBlankLesson(this.motion);
      }
      this.state = LessonCreationState.ModifyLesson;
    },
    addActivity(targetIndex?: number) {
      const newActivity: Activity = {
        title: `Activity ${this.lessonUnderConstruction.activities.length + 1}`,
        startTime: 0,
        endTime: this.typedMotion.duration,
        demoVisual: 'video',
        userVisual: 'none',
      };

      if (targetIndex === undefined) {
        this.lessonUnderConstruction.activities.push(newActivity);
        this.activeActivityIndex = this.lessonUnderConstruction.activities.length - 1;
      } else {
        this.lessonUnderConstruction.activities.splice(targetIndex, 0, newActivity);
        this.activeActivityIndex = targetIndex;
      }
    },
    selectActivity(targetIndex: number) {
      this.activeActivityIndex = targetIndex;
    },
  },
});
</script>

<style lang="scss">

.center-block {
  display: inline-block;
  margin-left: auto;
  margin-right: auto;
}

</style>
