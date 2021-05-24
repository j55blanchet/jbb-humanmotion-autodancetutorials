<template>
    <teleport to="#topbarLeft">

    </teleport>

    <section class="section create-lesson-screen">
      <div class="hero is-primary block">
        <div class="hero-body">
          <div class="container">
            <p class="title">
              Lesson Creation
            </p>
            <p class="subtitle">
              <span v-if="state === LessonCreationState.SelectOpenState">Tempalte Selection</span>
              <span v-else>Editing &quot;{{lessonUnderConstruction.header.lessonTitle}}&quot;</span>
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
              <li>
                <a @click="activeLessonSelectionIndex = -1"
                  :class="{'is-active': activeLessonSelectionIndex === -1}">(start from scratch)</a>
              </li>
              <li v-for="(lesson, i) in lessons" :key="lesson._id">
                <a @click="activeLessonSelectionIndex = i" :class="{'is-active': activeLessonSelectionIndex === i}">
                  <strong>#{{i+1}}</strong>&nbsp;{{lesson.header.lessonTitle}}
                </a>
              </li>
            </ul>
          </div>
          <div class="card-footer" v-if="canEditActiveLesson">
            <a class="card-footer-item" @click="startCreation(false)">Edit</a>
          </div><div class="card-footer">
            <a class="card-footer-item" @click="startCreation(true)">
              <span v-if="activeLessonSelectionIndex === -1">Start New</span>
              <span v-else>Use as Template</span>
            </a>
          </div>
        </div>
      </div>

      <div v-if="state === LessonCreationState.ModifyLesson" class="block">
        <div class="columns is-multiline is-centered">
          <div class="column is-narrow">
            <div class="box">
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

              <div class="field">
                <label class="label">Segments</label>
                <div class="control block">
                  <SegmentedProgressBar
                  :segments="progressSegments"
                    :progress="motion.duration"
                    :enableAll="true"/>
                  </div>
                  <div class="control block">
                    <div class="block">
                      <span class="m-1" v-for="(segBreak, i) in lessonUnderConstruction.segmentBreaks" :key="i">
                        <input
                            class="input narrow-number-input"
                            :key="i"
                            type="number"
                            v-model="lessonUnderConstruction.segmentBreaks[i]"
                            :min="lessonUnderConstruction.segmentBreaks[i - 1] ?? 0"
                            :step="0.01"
                            :max="lessonUnderConstruction.segmentBreaks[i + 1] ?? motion.duration" />
                      </span>
                    </div>
                    <div class="block has-text-right">
                      <!-- <span>Add New</span> -->
                      <input
                          class="input narrow-number-input is-info"
                          type="number"
                          v-model="newSegmentVal"
                          :min="0"
                          :step="0.01"
                          :max="motion.duration" />
                      <button class="ml-1 button is-info is-light" @click="addSegmentBreak(newSegmentVal)">Add Segment</button>
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
              <div class="field is-grouped is-grouped-right">
                <div class="control" v-if="canDeleteLesson">
                  <button class="button is-danger is-outlined" @click="deleteLesson">
                    Delete
                  </button>
                </div>
                <div class="control">
                  <button class="button" @click="exportLesson">Export</button>
                </div>
                <div class="control">
                  <button class="button is-primary" @click="saveLesson">
                    <span v-if="lessonInDatabase">Update</span>
                    <span v-else>Save</span>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <div class="column is-narrow">
            <div class="box">
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
                  <label class="label">Playback Speed</label>
                </div>
                <div class="field-body">
                  <div class="field is-narrow">
                    <div class="control">
                      <input type="number" class="input narrow-number-input" v-model.number="activeActivity.practiceSpeed" min="0" step="0.01" :max="2">
                    </div>
                  </div>
                </div>
              </div>

              <div class="field is-horizontal">
                <div class="field-label">
                  <label class="label">Start Time</label>
                </div>
                <div class="field-body">
                  <div class="field is-narrow">
                    <div class="control">
                      <input type="number" class="input narrow-number-input" v-model.number="activeActivity.startTime" min="0" step="0.01" :max="motion.duration">
                    </div>
                  </div>
                  <div class="field">
                    <div class="control">
                      <input type="range" class="input slider mt-0 mb-0" v-model.number="activeActivity.startTime" min="0" step="0.01" :max="motion.duration"/>
                    </div>
                  </div>
                </div>
              </div>

              <div class="field is-horizontal">
                <div class="field-label">
                  <label class="label">End Time</label>
                </div>
                <div class="field-body">
                  <div class="field is-narrow">
                    <div class="control">
                      <input type="number" class="input narrow-number-input" v-model.number="activeActivity.endTime" :min="0" step="0.01" :max="motion.duration">
                    </div>
                  </div>
                  <div class="field">
                    <div class="control">
                      <input type="range" class="input slider mt-0 mb-0" v-model.number="activeActivity.endTime" :min="0" step="0.01" :max="motion.duration"/>
                    </div>
                  </div>
                </div>
              </div>

              <div class="field is-horizontal">
                <div class="field-label">
                  <label class="label">Start Instruction</label>
                </div>
                <div class="field-body">
                  <div class="field">
                    <div class="control">
                      <input type="text" class="input" v-model="activeActivity.startInstruction" />
                    </div>
                  </div>
                </div>
              </div>

              <div class="field is-horizontal">
                <div class="field-label">
                  <label class="label">Playing Instruction</label>
                </div>
                <div class="field-body">
                  <div class="field">
                    <div class="control">
                      <input type="text" class="input" v-model="activeActivity.playingInstruction" />
                    </div>
                  </div>
                </div>
              </div>

              <div class="field is-horizontal">
                <div class="field-label">
                  <label class="label">End Instruction</label>
                </div>
                <div class="field-body">
                  <div class="field">
                    <div class="control">
                      <input type="text" class="input" v-model="activeActivity.endInstruction" />
                    </div>
                  </div>
                </div>
              </div>

              <div class="field is-horizontal">
                <div class="field-label">
                  <label class="label">Static Instruction</label>
                </div>
                <div class="field-body">
                  <div class="field">
                    <div class="control">
                      <input type="text" class="input" v-model="activeActivity.staticInstruction" />
                    </div>
                  </div>
                </div>
              </div>

              <div class="field is-horizontal">
                <div class="field-label">
                  <label class="label">Pauses</label>
                </div>
                <div class="field-body">
                  <div class="field">
                    <div class="control">
                      <ul class="menu-list">
                        <li v-for="(pause, i) in activeActivity.pauses ?? []" :key="i">
                          <a :class="{'is-active': activePauseIndex === i}" @click="selectPause(i)">
                            <strong>#{{i+1}}</strong>
                            for {{pause.pauseDuration ?? Constants.DefaultPauseDuration}}s
                            @ {{pause.time}}s
                            <small v-if="pause.instruction">&quot;{{pause.instruction}}&quot;</small>
                          </a>
                        </li>
                        <li v-if="lessonUnderConstruction.activities.length === 0">No Pauses</li>
                        <li><a @click="addPause()">&plus; Add Pause</a></li>
                        <li v-show="(activeActivity.pauses?.length ?? 0) >= 2"><a @click="sortPauses()">Sort Pauses</a></li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>

              <div class="field is-horizontal">
                <div class="field-label">
                  <label class="label">Timed Instructions</label>
                </div>
                <div class="field-body">
                  <div class="field">
                    <div class="control">
                      <ul class="menu-list">
                        <li v-for="(ti, i) in activeActivity.timedInstructions ?? []" :key="i">
                          <a :class="{'is-active': activeTimedInstructionIndex === i}" @click="selectTimedInstruction(i)">
                            <strong>#{{i+1}}</strong>&nbsp;
                            <small>&quot;{{ti.text}}&quot;</small>
                            from {{ti.startTime}}s
                            to {{ti.endTime}}s
                          </a>
                        </li>
                        <li v-if="lessonUnderConstruction.activities.length === 0">No Timed Instructions</li>
                        <li><a @click="addTimedInstruction()">&plus; Add Timed Instruction</a></li>
                        <li v-show="(activeActivity.timedInstructions?.length ?? 0) >= 2"><a @click="sortTimedInstructions()">Sort Timed Instructions</a></li>
                        <li v-if="lessonUnderConstruction.activities.length === 0">No Timed Instructions</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="column is-narrow">

            <div v-if="activePause" class="box">
              <h6 class="title is-5">Pause {{activePauseIndex + 1}} Details</h6>
              <div class="field is-horizontal">
                <div class="field-label"><label class="label">Time</label></div>
                <div class="field-body">
                  <div class="field is-narrow">
                    <div class="control">
                      <input type="number" class="input narrow-number-input" v-model.number="activePause.time" min="0" step="0.01" :max="motion.duration">
                    </div>
                  </div>
                  <div class="field">
                    <div class="control">
                      <input type="range" class="input slider mt-0 mb-0" v-model.number="activePause.time" min="0" step="0.01" :max="motion.duration"/>
                    </div>
                  </div>
                </div>
              </div>
              <div class="field is-horizontal">
                <div class="field-label">
                  <label class="label">Duration</label>
                </div>
                <div class="field-body">
                  <div class="field is-narrow">
                    <div class="control">
                      <input type="number" class="input narrow-number-input" v-model.number="activePause.pauseDuration" min="0" step="0.01" :max="10">
                    </div>
                  </div>
                </div>
              </div>
              <div class="field is-horizontal">
                <div class="field-label">
                  <label class="label">Instruction</label>
                </div>
                <div class="field-body">
                  <div class="field">
                    <div class="control">
                      <input type="text" class="input" v-model="activePause.instruction">
                    </div>
                  </div>
                </div>
              </div>
              <div class="field">
                <div class="control">
                  <button class="button is-danger is-outlined" @click="deletePause(activePause)">Remove Pause {{activePauseIndex + 1}}</button>
                </div>
              </div>
            </div> <!-- End pause detail section-->

            <div v-if="activeTimedInstruction" class="box">
              <h6 class="title is-5">Timed Instruction {{activeTimedInstructionIndex + 1}} Details</h6>
              <div class="field is-horizontal">
                <div class="field-label"><label class="label">Start Time</label></div>
                <div class="field-body">
                  <div class="field is-narrow">
                    <div class="control">
                      <input type="number" class="input narrow-number-input" v-model.number="activeTimedInstruction.startTime" :min="activeActivity.startTime" step="0.01" :max="activeTimedInstruction.endTime">
                    </div>
                  </div>
                  <div class="field">
                    <div class="control">
                      <input type="range" class="input slider mt-0 mb-0" v-model.number="activeTimedInstruction.startTime" :min="activeActivity.startTime" step="0.01" :max="activeActivity.endTime"/>
                    </div>
                  </div>
                </div>
              </div>
              <div class="field is-horizontal">
                <div class="field-label"><label class="label">End Time</label></div>
                <div class="field-body">
                  <div class="field is-narrow">
                    <div class="control">
                      <input type="number" class="input narrow-number-input" v-model.number="activeTimedInstruction.endTime" :min="activeTimedInstruction.startTime" step="0.01" :max="activeActivity.endTime">
                    </div>
                  </div>
                  <div class="field">
                    <div class="control">
                      <input type="range" class="input slider mt-0 mb-0" v-model.number="activeTimedInstruction.endTime" :min="activeActivity.startTime" step="0.01" :max="activeActivity.endTime"/>
                    </div>
                  </div>
                </div>
              </div>
              <div class="field is-horizontal">
                <div class="field-label">
                  <label class="label">Text</label>
                </div>
                <div class="field-body">
                  <div class="field">
                    <div class="control">
                      <input type="text" class="input" v-model="activeTimedInstruction.text">
                    </div>
                  </div>
                </div>
              </div>
              <div class="field">
                <div class="control">
                  <button class="button is-danger is-outlined" @click="deleteTimedInstruction(activeTimedInstruction)">Remove Timed Instruction {{activeTimedInstructionIndex + 1}}</button>
                </div>
              </div>
            </div> <!-- End timed instruction detail section-->
          </div>

          <div class="column is-narrow">
            <div class="box">
              <h5 class="title is-5">Demo</h5>

              <ActivityVideoPlayer
                class="block"
                ref="activityVideoPlayer"
                :motion="motion"
                :lesson="lessonUnderConstruction"
                :activity="activeActivity"
                :maxHeight="'400px'"
                @progress="onProgress" />

              <SegmentedProgressBar
                class="block"
                :segments="progressSegments"
                :progress="activityProgress"/>

              <div class="buttons is-centered has-addons">
                <button class="button" :disabled="!hasPreviousActivity" @click="activeActivityIndex -= 1">&lt;</button>
                <button class="button is-primary" :disabled="!($refs.activityVideoPlayer?.awaitingStart ?? false)" @click="playDemo">Play Activity</button>
                <button class="button" :disabled="!($refs.activityVideoPlayer?.activityFinished ?? false)" @click="$refs.activityVideoPlayer?.reset()">Reset</button>
                <button class="button" :disabled="!hasNextActivity" @click="activeActivityIndex += 1">&gt;</button>
              </div>
            </div>
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
  defineComponent, ref, toRefs, watchEffect,
} from 'vue';

import Constants from '@/services/Constants';
import ActivityVideoPlayer from '@/components/elements/ActivityVideoPlayer.vue';
import PausingVideoPlayer from '@/components/elements/PausingVideoPlayer.vue';
import VideoPlayer from '@/components/elements/VideoPlayer.vue';
import db, { createBlankActivity, createBlankLesson, DatabaseEntry } from '@/services/MotionDatabase';
import DanceLesson, { Activity, PauseInfo, TimedInstruction } from '@/model/DanceLesson';
import Utils from '@/services/Utils';
import SegmentedProgressBar, { ProgressSegmentData, calculateProgressSegments } from '@/components/elements/SegmentedProgressBar.vue';

const LessonCreationState = Object.freeze({
  SelectOpenLesson: 'SelectOpenLesson',
  ModifyLesson: 'ModifyLesson',
});

export default defineComponent({
  name: 'CreateLessonScreen',
  components: {
    ActivityVideoPlayer,
    SegmentedProgressBar,
    // VideoPlayer,
    // ActivityVideoPlayer,
    // VideoPlayer,
  },
  props: ['motion'],
  emits: ['back-selected', 'lesson-created'],
  data() {
    return {
      newPauseTime: 0,
      newSegmentVal: 0,
      activeLessonSelectionIndex: -1,
      activePauseIndex: 0,
      activeTimedInstructionIndex: 0,
      activityProgress: 0,
    };
  },
  computed: {
    activeLessonSelection(): DanceLesson | null {
      return this.lessons[this.activeLessonSelectionIndex] ?? null;
    },
    lessonInDatabase(): boolean {
      return db.hasLesson(this.lessonUnderConstruction);
    },
    canDeleteLesson(): boolean {
      return this.lessonInDatabase && this.lessonUnderConstruction.source === 'custom';
    },
    lessonStartTime(): number {
      return this.lessonUnderConstruction?.segmentBreaks[0] ?? 0;
    },
    lessonEndTime(): number {
      return this.lessonUnderConstruction.segmentBreaks[this.lessonUnderConstruction.segmentBreaks.length - 1] ?? this.motion?.duration ?? 1;
    },
    lessons() {
      if (!this.motion) return [];
      const motion = this.motion as DatabaseEntry;
      const lessons = db.getLessons(motion);
      return lessons ?? [];
    },
    progressSegments(): ProgressSegmentData[] {
      if (this.activeActivity && this.lessonUnderConstruction) return calculateProgressSegments(this.lessonUnderConstruction, this.activeActivity);
      return [];
    },
    activePause(): null | PauseInfo {
      return ((this as any).activeActivity.pauses ?? [])[(this as any).activePauseIndex] ?? null;
    },
    activeTimedInstruction(): null | TimedInstruction {
      return ((this as any).activeActivity.timedInstructions ?? [])[(this as any).activeTimedInstructionIndex] ?? null;
    },
    hasNextActivity(): boolean {
      return this.activeActivityIndex + 1 < this.lessonUnderConstruction.activities.length;
    },
    hasPreviousActivity(): boolean {
      return this.activeActivityIndex > 0;
    },
    canEditActiveLesson() {
      const acLes = this.activeLessonSelection as DanceLesson;
      return acLes?.source === 'custom';
    },
  },
  mounted() {
    if (this.lessons.length === 0) {
      this.startCreation(true);
    }
  },
  setup(props) {
    const { motion } = toRefs(props);
    const typedMotion = computed(() => motion.value as unknown as DatabaseEntry);
    const state = ref(LessonCreationState.SelectOpenLesson);
    const lessonUnderConstruction = ref(createBlankLesson(motion));
    const activeActivityIndex = ref(0);
    const activeActivity = computed(() => lessonUnderConstruction.value.activities[activeActivityIndex.value]);

    watchEffect(() => {
      if (activeActivity.value.startTime < 0) activeActivity.value.startTime = 0;
      if (activeActivity.value.endTime > motion.value.duration) activeActivity.value.endTime = motion.value.duration;
      if (+activeActivity.value.endTime < +activeActivity.value.startTime) activeActivity.value.endTime = activeActivity.value.startTime;
    });

    return {
      state,
      typedMotion,
      LessonCreationState,
      lessonUnderConstruction,
      activeActivityIndex,
      activeActivity,
      Constants,
    };
  },
  methods: {
    startCreation(asTemplate: boolean) {
      const existingLesson = this.activeLessonSelection;
      if (existingLesson && asTemplate) {
        console.log('Creating new lesson from template');
        this.lessonUnderConstruction = Utils.deepCopy(existingLesson);
        this.lessonUnderConstruction._id = Utils.uuidv4();
      } else if (existingLesson && !asTemplate) {
        console.log('Editing existing lesson');
        this.lessonUnderConstruction = existingLesson;
      } else {
        console.log('Creating new lesson from scratch');
        this.lessonUnderConstruction = createBlankLesson(this.motion);
      }
      this.state = LessonCreationState.ModifyLesson;
    },
    addActivity(targetIndex?: number) {
      const newActivity: Activity = createBlankActivity(this.typedMotion, `Activity ${this.lessonUnderConstruction.activities.length + 1}`);

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
    addPause(targetIndex?: number) {
      const pauses = this.activeActivity.pauses ?? [];
      const newPause: PauseInfo = {
        time: this.activeActivity.startTime,
        pauseDuration: Constants.DefaultPauseDuration,
      };
      if (targetIndex === undefined) {
        pauses.push(newPause);
        this.activePauseIndex = pauses.length - 1;
      } else {
        pauses.splice(targetIndex, 0, newPause);
        this.activePauseIndex = targetIndex;
      }
      this.sortPauses();
      this.activeActivity.pauses = pauses;
    },
    selectPause(targetIndex: number) {
      if (targetIndex === this.activePauseIndex) this.activePauseIndex = -1;
      else this.activePauseIndex = targetIndex;
    },
    sortPauses() {
      const pauses = this.activeActivity.pauses ?? [];
      const selectedPause = pauses[this.activePauseIndex];
      pauses.sort((a, b) => a.time - b.time);
      const newIndex = pauses.indexOf(selectedPause);
      if (newIndex >= 0) this.activePauseIndex = newIndex;
      this.activeActivity.pauses = pauses;
    },
    deletePause(pauseObj: PauseInfo) {
      const pauses = this.activeActivity.pauses ?? [];
      const pauseIndex = pauses.indexOf(pauseObj);
      // eslint-disable-next-line no-alert
      if (pauseIndex >= 0 && window.confirm('Are you sure you want to delete this pause?')) pauses.splice(pauseIndex, 1);
      this.activeActivity.pauses = pauses;
    },
    addTimedInstruction(targetIndex?: number) {
      const timedInstructions = this.activeActivity.timedInstructions ?? [];
      const newInstruction: TimedInstruction = {
        startTime: 0,
        endTime: 1,
        text: 'Do XYZ',
      };
      if (targetIndex === undefined) {
        timedInstructions.push(newInstruction);
        this.activeTimedInstructionIndex = timedInstructions.length - 1;
      } else {
        timedInstructions.splice(targetIndex, 0, newInstruction);
        this.activeTimedInstructionIndex = targetIndex;
      }
      this.sortTimedInstructions();

      this.activeActivity.timedInstructions = timedInstructions;
    },
    selectTimedInstruction(targetIndex: number) {
      if (targetIndex === this.activeTimedInstructionIndex) this.activeTimedInstructionIndex = -1;
      else this.activeTimedInstructionIndex = targetIndex;
    },
    sortTimedInstructions() {
      const timedInstructs = this.activeActivity.timedInstructions ?? [];
      const selectedTimedInstruc = timedInstructs[this.activeTimedInstructionIndex];
      timedInstructs.sort((a, b) => a.startTime - b.startTime);
      const newIndex = timedInstructs.indexOf(selectedTimedInstruc);
      if (newIndex >= 0) this.activeTimedInstructionIndex = newIndex;
      this.activeActivity.timedInstructions = timedInstructs;
    },
    deleteTimedInstruction(timedInstruction: TimedInstruction) {
      const timedInstructs = this.activeActivity.timedInstructions ?? [];
      const tiIndex = timedInstructs.indexOf(timedInstruction);
      // eslint-disable-next-line no-restricted-globals, no-alert
      if (tiIndex >= 0 && window.confirm('Are you sure you want to delete this timed instruction?')) timedInstructs.splice(tiIndex, 1);
      this.activeActivity.timedInstructions = timedInstructs;
    },
    addSegmentBreak(breakTime: number) {
      breakTime = +breakTime;
      if (Number.isNaN(breakTime) || breakTime < 0 || breakTime > this.motion.duration) return;
      this.lessonUnderConstruction.segmentBreaks.push(breakTime);
      const newList = this.lessonUnderConstruction.segmentBreaks.sort();
      this.lessonUnderConstruction.segmentBreaks = newList;
      this.newSegmentVal = 0;
    },
    playDemo() {
      (this.$refs.activityVideoPlayer as any).play();
    },
    onProgress(progress: number) {
      this.activityProgress = progress;
    },
    saveLesson() {
      db.saveCustomLesson(this.lessonUnderConstruction);
    },
    deleteLesson() {
      // eslint-disable-next-line no-alert
      if (!window.confirm('Are you sure you want to delete this lesson?')) {
        return;
      }

      db.deleteCustomLesson(this.lessonUnderConstruction);
      this.$emit('back-selected');
    },
    exportLesson() {
      Utils.PromptDownloadFile(`${this.lessonUnderConstruction.header.lessonTitle}.lesson.json`, JSON.stringify(this.lessonUnderConstruction));
    },
  },
});
</script>

<style lang="scss">

.create-lesson-screen {
  .center-block {
    display: inline-block;
    margin-left: auto;
    margin-right: auto;
  }

  .narrow-number-input {
    max-width: 5.5rem;
  }

  .seg-break {
    background: white;
  }
}

</style>
