<template>
  <div class="card lesson-card" v-if="dance">
    <div class="card-header">
      <h4 class="card-header-title">
        {{ dance.title }}
      </h4>

      <a class="card-header-icon" @click="$emit('closed')">
        <i class="fas fa-times"></i>
      </a>
    </div>
    <div class="card-content">
      <div class="columns">
        <div class="column is-narrow is-hidden-mobile">
          <video :src="dance.videoSrc" autoplay="true" muted="true" width="180" />
        </div>
        <div class="column">
          <div class="menu">
            <p class="menu-label">
              Pick a lesson
            </p>
            <ul class="menu-list">
              <li v-for="lesson in dance.lessons" :key="lesson._id">
                <a @click="$emit('lesson-selected', {dance: dance, lesson: lesson})">
                  {{ lesson.header.lessonTitle }}
                </a>
              </li>
            </ul>
            <p v-if="dance.lessons.length == 0">No lessons available.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'LessonCard',
  props: ['dance'],
  emits: ['lesson-selected', 'closed'],
});
</script>

<style lang="scss">

.lesson-card .dance-image {
  max-height: 50vh;
}

</style>
