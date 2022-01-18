<template>
  <div class="card lesson-card" v-if="motion">
    <div class="card-header">
      <h4 class="card-header-title">
        {{ motion.title }}
      </h4>

      <a class="card-header-icon" @click="$emit('closed')">
        <i class="fas fa-times"></i>
      </a>
    </div>
    <div class="card-content">
      <div class="columns">
        <div class="column is-narrow is-hidden-mobile">
          <video :src="motion.videoSrc" autoplay="true" muted="true" width="180" />
        </div>
        <div class="column">
          <div class="menu">
            <p class="menu-label">
              Pick a mini-lesson
            </p>
            <ul class="menu-list">
              <li v-for="lesson in lessons" :key="lesson._id">
                <a @click="$emit('lesson-selected', motion, lesson)">
                  {{ lesson.header.lessonTitle }}
                </a>
              </li>
              <li v-if="canCreateLesson">
                <a @click="$emit('create-lesson-selected', motion)">Create Lesson</a>
              </li>
              <li v-for="(kfopt, i) in keyframeOptions" :key="i">
                <a @click="$emit('keyframeselectortool-selected', motion, kfopt.keyframes)">Keyframes - {{kfopt.title}}</a>
              </li>
              <li>
                <a @click="$emit('keyframeselectortool-selected', motion, [])">Select Keyframes</a>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import db, { DatabaseEntry } from '@/services/MotionDatabase';
import keyframeOptions from '@/data/keyframeOptions.json';

export default defineComponent({
  name: 'LessonCard',
  props: {
    motion: {
      type: Object,
    },
    canCreateLesson: {
      type: Boolean,
      default: true,
    },
  },
  computed: {
    lessons() {
      if (!this.motion) return [];
      const motion = this.motion as DatabaseEntry;
      const lessons = db.getLessons(motion);
      return lessons ?? [];
    },
    keyframeOptions() {
      if (!this.motion) return [];
      const motion = this.motion as DatabaseEntry;
      return keyframeOptions.filter((option) => option.clipName === motion.clipName);
    },
  },
  emits: ['lesson-selected', 'create-lesson-selected', 'closed', 'keyframeselectortool-selected'],
});
</script>

<style lang="scss">

.lesson-card .dance-image {
  max-height: 50vh;
}

</style>
