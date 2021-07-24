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
              <span v-if="state === LessonCreationState.SelectOpenLesson">Template Selection</span>
              <span v-else>Editing &quot;{{lessonUnderConstruction.header.lessonTitle}}&quot;</span>
            </p>
          </div>
        </div>
      </div>

      <div class="container block">
        <div class="buttons is-centered has-addons">
          <button v-if="showBackButton" class="button" :class="{'is-danger': isDirty, 'is-outlined': isDirty, 'is-primary': !isDirty}" @click="goBack">&lt; Back</button>
          <button v-if="showCloseButton" class="button" :class="{'is-danger': isDirty, 'is-outlined': isDirty, 'is-primary': !isDirty}" @click="goBack"><i class="fa fa-close"></i> Close</button>
          <button v-if="state === LessonCreationState.ModifyLesson && canDeleteLesson" class="button is-danger is-outlined" @click="deleteLesson">
            Delete
          </button>
          <button v-if="state === LessonCreationState.ModifyLesson && showExportButton" class="button" @click="exportLesson">Export</button>
          <button v-if="state === LessonCreationState.ModifyLesson" class="button" :class="{'is-primary': isDirty}" :disabled="!isDirty" @click="saveLesson">
            <span v-if="lessonInDatabase">Update</span>
            <span v-else>Save</span>
          </button>
        </div>
      </div>

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
          <div class="card-footer" v-if="canEditActiveLesson && !disableEditingExisting">
            <p v-if="disableEditingExisting" class="card-footer-item">Editing disabled</p>
            <a v-else class="card-footer-item" @click="startCreation(false)">Edit</a>
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
          <div class="column is-half is-one-third-widescreen is-one-quarter-fullhd">
            <div class="box">
              <h5 class="title is-5">Lesson</h5>

              <div class="field is-horizontal">
                <div class="field-label is-normal">
                  <label class="label">Id</label>
                </div>
                <div class="field-body">
                  <div class="field">
                    <div class="control">
                      <input class="input" disabled type="text" :value="lessonUnderConstruction._id">
                    </div>
                  </div>
                </div>
              </div>

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
                      <div class="field has-addons is-inline-block m-1" v-for="(segBreak, i) in lessonUnderConstruction.segmentBreaks" :key="i">
                        <span class="control">
                          <input
                              class="input narrow-number-input is-small"
                              :key="i"
                              type="number"
                              :value="lessonUnderConstruction.segmentBreaks[i].toFixed(2)"
                              @input="setSegmentBreak(i, $event)"
                              :min="0"
                              :step="0.01"
                              :max="motion.duration" />
                          </span>
                          <span class="control">
                            <button class="button is-danger is-small is-light" :disabled="!canDeleteSegment(i)" @click="removeSegmentBreak(i)">
                              <span class="icon">
                                <i class="fas fa-times"></i>
                              </span>
                            </button>
                          </span>
                      </div>
                    </div>
                    <div class="block has-text-right">
                      <!-- <span>Add New</span> -->
                      <input
                          class="input narrow-number-input is-info"
                          type="number"
                          v-model.number="newSegmentVal"
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
                        <li v-if="activeActivity"><a @click="duplicateActivity()"><span class="icon"><i class="far fa-copy"></i></span><span>Duplicate</span></a></li>
                        <li><a @click="addActivity()">&plus; Add Activity</a></li>
                        <li v-if="lessonUnderConstruction.activities.length === 0">No Activities</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="column is-half is-one-third-widescreen is-one-quarter-fullhd">
            <div class="box">
              <h5 class="title is-5">Activity</h5>

              <div class="field is-horizontal">
                <div class="field-label is-normal">
                  <label class="label">Order</label>
                </div>
                <div class="field-body">
                  <div class="field has-addons">
                    <div class="control">
                      <button class="button" :disabled="!canReorderActivity(activeActivityIndex, -1)" @click="reorderActivity(activeActivityIndex, -1)">
                        <div class="icon"><i class="fas fa-chevron-down"></i></div>
                      </button>
                    </div>
                    <div class="control is-expanded">
                      <input class="input" type="text" disabled :value="activeActivityIndex + 1">
                    </div>
                    <div class="control">
                      <button class="button" :disabled="!canReorderActivity(activeActivityIndex, 1)" @click="reorderActivity(activeActivityIndex, 1)">
                        <div class="icon"><i class="fas fa-chevron-up"></i></div>
                      </button>
                    </div>
                  </div>
                </div>
              </div>

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
                  <label class="label">Focused Segments</label>
                </div>
                <div class="field-body">
                  <div class="field">
                    <div v-for="(segInfo, i) in activeActivityFocusedSegments" :key="i">
                      <label class="checkbox">
                        <input type="checkbox" :checked="activeActivityFocusedSegments[i].isFocused" @input="setFocusedSegment(i, $event)">&nbsp;<strong>{{i+1}}</strong>: <code>{{segInfo.startTime.toFixed(2)}}</code>-<code>{{segInfo.endTime.toFixed(2)}}</code>
                      </label>
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
                  <label class="label">Mode</label>
                </div>
                <div class="field-body">
                  <div class="field">
                    <div class="control">
                      <div class="select">
                        <select v-model="displayMode">
                          <option value="other" disabled>Other</option>
                          <option value="video-demo">Video Demo</option>
                          <option value="skeleton-overlay">Skeleton Overlay</option>
                        </select>
                      </div>
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
                            at <span class="is-underlined">{{pause.time.toFixed(2)}}</span>
                            for <span class="is-underlined">{{(pause.pauseDuration ?? Constants.DefaultPauseDuration).toFixed(2)}}</span>s
                            <small v-if="pause.instruction">&nbsp; : &nbsp;<span>&quot;{{pause.instruction}}&quot;</span></small>
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
                            from <span class="is-underlined">{{ti.startTime.toFixed(2)}}</span>s
                            to <span class="is-underlined">{{ti.endTime.toFixed(2)}}</span>s
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

              <div class="block buttons is-right">
                <button class="button is-outlined is-danger" :disabled="!canDeleteActivity(activeActivityIndex)" @click="deleteActivity(activeActivityIndex)">Delete Activity #{{activeActivityIndex + 1}}</button>
              </div>
            </div>
          </div>

          <div class="column is-half is-one-third-widescreen is-one-quarter-fullhd"
               v-if="activePause || activeTimedInstruction">
            <div v-if="activePause" class="box">
              <h6 class="title is-5">Pause {{activePauseIndex + 1}} Details</h6>
              <div class="field is-horizontal">
                <div class="field-label"><label class="label">Time</label></div>
                <div class="field-body">
                  <div class="field is-narrow">
                    <div class="control">
                      <input type="number" class="input narrow-number-input" v-model.number="activePause.time" :min="activeActivity.startTime" step="0.01" :max="activeActivity.endTime">
                    </div>
                  </div>
                  <div class="field">
                    <div class="control">
                      <input type="range" class="input slider mt-0 mb-0" v-model.number="activePause.time" :min="activeActivity.startTime" step="0.01" :max="activeActivity.endTime"/>
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

          <div class="column is-half-tablet is-half-desktop is-one-third-widescreen is-one-quarter-fullhd">
            <div class="box">
              <h5 class="title is-5">Demo</h5>

              <div class="image is-square">
                <!-- <div style="height:400px;width:100%;"> -->
                  <MiniLessonPlayer
                   class="is-overlay"
                    ref="miniLessonPlayer"
                    @activity-changed="selectActivity"
                    :videoEntry="motion"
                    :miniLesson="lessonUnderConstruction"
                    :enableCompleteLesson="false"
                  />
                <!-- </div> -->
              </div>
            <!--
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
              </div> -->
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
  defineComponent, nextTick, ref, toRefs, watchEffect,
} from 'vue';

import Constants from '@/services/Constants';
import MiniLessonPlayer from '@/components/elements/MiniLessonPlayer.vue';
import db, { createBlankActivity, createBlankLesson, DatabaseEntry } from '@/services/MotionDatabase';
import MiniLesson, { MiniLessonActivity, PauseInfo, TimedInstruction } from '@/model/MiniLesson';
import Utils from '@/services/Utils';
import SegmentedProgressBar, { ProgressSegmentData, calculateProgressSegments } from '@/components/elements/SegmentedProgressBar.vue';

const LessonCreationState = Object.freeze({
  SelectOpenLesson: 'SelectOpenLesson',
  ModifyLesson: 'ModifyLesson',
});

interface SegmentInfo {
  isFocused: boolean;
  startTime: number;
  endTime: number;
}

export default defineComponent({
  name: 'CreateLessonScreen',
  components: {
    MiniLessonPlayer,
    SegmentedProgressBar,
  },
  props: {
    motion: {
      type: Object,
      required: true,
    },
    saveReference: {
      type: Boolean,
      default: true,
    },
    showBackButton: {
      type: Boolean,
      default: true,
    },
    showCloseButton: {
      type: Boolean,
      default: false,
    },
    showExportButton: {
      type: Boolean,
      default: true,
    },
    lessonToEdit: {
      type: Object,
      default: null,
    },
    saveToDatabase: {
      type: Boolean,
      default: true,
    },
    disableEditingExisting: {
      type: Boolean,
      default: false,
    },
  },
  emits: ['back-selected', 'lesson-saved'],
  data() {
    return {
      newPauseTime: 0,
      newSegmentVal: 0,
      activeLessonSelectionIndex: -1,
      activePauseIndex: 0,
      activeTimedInstructionIndex: 0,
      // activityProgress: 0,
    };
  },
  computed: {
    displayMode: {
      get() {
        const demoVisual = this.activeActivity.demoVisual ?? 'video';
        const userVisual = this.activeActivity.userVisual ?? 'none';
        if (demoVisual === 'video' && userVisual === 'none') return 'video-demo';
        if (demoVisual === 'skeleton' && userVisual === 'video') return 'skeleton-overlay';
        return 'other';
      },
      set(newVal: 'other' | 'video-demo' | 'skeleton-overlay') {
        if (newVal === 'video-demo') {
          this.activeActivity.demoVisual = 'video';
          this.activeActivity.userVisual = 'none';
        } else if (newVal === 'skeleton-overlay') {
          this.activeActivity.demoVisual = 'skeleton';
          this.activeActivity.userVisual = 'video';
        }
      },
    },
    activeActivityFocusedSegments() {
      const segBreaks = (this as any).lessonUnderConstruction.segmentBreaks as number[];
      const segs: number[] = (this as any).activeActivity?.focusedSegments ?? [];
      const segsSet = new Set(segs);
      const boolArray = Utils.range((this as any).lessonUnderConstruction.segmentBreaks.length - 1)
        .map((i) => ({
          isFocused: segsSet.has(i),
          startTime: segBreaks[i],
          endTime: segBreaks[i + 1],
        } as SegmentInfo));
      return boolArray;
    },
    activeLessonSelection(): MiniLesson | null {
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
      const acLes = this.activeLessonSelection as MiniLesson;
      return acLes?.source === 'custom';
    },
  },
  mounted() {
    const passedInLesson = this.$props.lessonToEdit as MiniLesson | null;
    if (passedInLesson) {
      console.log('CreateLessonScreen:: using passed in lesson', passedInLesson);
      this.startCreation(false, Utils.deepCopy(passedInLesson));
      nextTick(() => { this.isDirty = false; });
    } else if (this.lessons.length === 0) {
      console.log('CreateLessonScreen:: creating blank lesson (no templates available)');
      this.startCreation(true);
    }
  },
  setup(props) {
    const { motion } = toRefs(props);
    const isDirty = ref(false);
    const typedMotion = computed(() => motion.value as unknown as DatabaseEntry);
    const state = ref(LessonCreationState.SelectOpenLesson);
    const lessonUnderConstruction = ref(createBlankLesson(typedMotion.value));
    const activeActivityIndex = ref(0);
    const activeActivity = computed(() => lessonUnderConstruction.value.activities[activeActivityIndex.value]);

    watchEffect(() => {
      if (activeActivity.value.startTime < 0) activeActivity.value.startTime = 0;
      if (activeActivity.value.endTime > motion.value.duration) activeActivity.value.endTime = motion.value.duration;
      if (+activeActivity.value.endTime < +activeActivity.value.startTime) activeActivity.value.endTime = activeActivity.value.startTime;
    });

    return {
      isDirty,
      state,
      typedMotion,
      LessonCreationState,
      lessonUnderConstruction,
      activeActivityIndex,
      activeActivity,
      Constants,
    };
  },
  watch: {
    activeActivityIndex: {
      handler(newVal: number) {
        (this.$refs.miniLessonPlayer as any).activeActivityIndex = newVal;
      },
    },
    lessonUnderConstruction: {
      handler() {
        this.isDirty = true;
      },
      deep: true,
    },
    'lessonUnderConstruction.segmentBreaks': {
      handler() {
        this.sortSegmentBreaks();
      },
      deep: true,
    },
    'activePause.time': {
      handler() {
        this.sortPauses();
      },
    },
    'activeTimedInstruction.startTime': {
      handler() {
        this.sortTimedInstructions();
      },
    },
  },
  methods: {
    canDeleteSegment(segmentIndex: number) {
      return this.progressSegments.length > 1;
    },
    goBack() {
      // eslint-disable-next-line no-alert
      if (!this.isDirty || window.confirm('Are you sure you want to go back without saving?')) {
        this.$emit('back-selected');
      }
    },
    startCreation(asTemplate: boolean, sourceLesson?: MiniLesson) {
      const existingLesson = sourceLesson ?? this.activeLessonSelection;
      if (existingLesson && asTemplate) {
        console.log('Creating new lesson from template');
        this.lessonUnderConstruction = Utils.deepCopy(existingLesson);
        this.lessonUnderConstruction._id = Utils.uuidv4();
        this.lessonUnderConstruction.source = 'custom';
      } else if (existingLesson && !asTemplate) {
        console.log('Editing existing lesson');
        this.lessonUnderConstruction = existingLesson;
        nextTick(() => { this.isDirty = false; });
      } else {
        console.log('Creating new lesson from scratch');
        this.lessonUnderConstruction = createBlankLesson(this.typedMotion);
      }
      this.state = LessonCreationState.ModifyLesson;
    },
    addActivity(targetIndex?: number) {
      const newActivity: MiniLessonActivity = createBlankActivity(this.typedMotion, `Activity ${this.lessonUnderConstruction.activities.length + 1}`);

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
    canDeleteActivity(targetIndex: number) {
      return this.lessonUnderConstruction.activities.length > 1;
    },
    canReorderActivity(targetIndex: number, indexDelta: number) {
      const curActivity = this.lessonUnderConstruction.activities[targetIndex];
      const swapActivity = this.lessonUnderConstruction.activities[targetIndex + indexDelta];
      return (curActivity !== undefined && swapActivity !== undefined);
    },
    reorderActivity(targetIndex: number, indexDelta: number) {
      const curActivity = this.lessonUnderConstruction.activities[targetIndex];
      const swapIndex = targetIndex + indexDelta;
      const swapActivity = this.lessonUnderConstruction.activities[swapIndex];
      if (curActivity === undefined || swapActivity === undefined) {
        console.error(`Cannot reorder activities ${targetIndex} and ${swapIndex}`);
        return;
      }

      this.lessonUnderConstruction.activities[swapIndex] = curActivity;
      this.lessonUnderConstruction.activities[targetIndex] = swapActivity;
      if (this.activeActivityIndex === targetIndex) {
        this.activeActivityIndex = swapIndex;
      }
    },
    deleteActivity(targetIndex: number) {
      const indexToDelete = targetIndex ?? this.activeActivityIndex;
      const activities = this.lessonUnderConstruction.activities ?? [];
      if (activities.length < 2) {
        console.error("Can't delete activity - no activities would be left");
        return;
      }
      // eslint-disable-next-line no-alert
      if (!window.confirm('Are you sure you want to delete this activity?')) return;
      console.log('Deleting activity at index', indexToDelete);
      activities.splice(indexToDelete, 1);
      this.lessonUnderConstruction.activities = activities;
      this.activeActivityIndex = Math.max(Math.min(activities.length - 1, this.activeActivityIndex), 0);
    },
    duplicateActivity() {
      const activity = this.activeActivity;
      const lesson = this.lessonUnderConstruction;
      if (!activity || !lesson) return;
      const dupActivity = Utils.deepCopy(activity);
      lesson.activities.splice(this.activeActivityIndex, 0, dupActivity);
      this.activeActivityIndex += 1;
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
      const newList = this.lessonUnderConstruction.segmentBreaks.sort((a, b) => a - b);
      this.lessonUnderConstruction.segmentBreaks = newList;
      this.newSegmentVal = 0;
    },
    setFocusedSegment(i: number, event: InputEvent) {
      const focusedSegments = this.activeActivity.focusedSegments ?? [];
      const curIndex = focusedSegments.indexOf(i);
      const isFocused: boolean = (event.target as any)?.checked ?? false;
      if (curIndex === -1 && isFocused) {
        focusedSegments.push(i);
        focusedSegments.sort();
      } else if (curIndex !== -1 && !isFocused) {
        focusedSegments.splice(curIndex, 1);
      }

      this.activeActivity.focusedSegments = focusedSegments;
    },
    sortSegmentBreaks() {
      this.lessonUnderConstruction.segmentBreaks = this.lessonUnderConstruction.segmentBreaks.sort((a, b) => a - b);
    },
    setSegmentBreak(i: number, event: InputEvent) {
      const val = parseFloat((event.target as any)?.value ?? '');
      if (!Number.isNaN(val) && val >= 0 && val <= this.motion.duration) {
        this.lessonUnderConstruction.segmentBreaks[i] = val;
      }
    },
    removeSegmentBreak(i: number) {
      this.lessonUnderConstruction.segmentBreaks.splice(i, 1);
    },
    // playDemo() {
    //   (this.$refs.activityVideoPlayer as any).play();
    // },
    // onProgress(progress: number) {
    //   this.activityProgress = progress;
    // },
    saveLesson() {
      if (this.$props.saveToDatabase) {
        db.saveCustomLesson(this.lessonUnderConstruction);
      }
      this.$emit('lesson-saved', this.lessonUnderConstruction);
      this.isDirty = false;
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
