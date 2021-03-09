<template>
  <div class="card" v-if="dance">
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
          <img :src="dance.animatedThumb" :alt="dance.title" class="dance-image" />
        </div>
        <div class="column">
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
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'LessonCard',
  props: ['dance'],
});
</script>

<style lang="scss" scoped>

.dance-image {
  max-height: 50vh;
}

</style>
