<template>
  <section class="section">
    <div class="container content has-text-centered is-hidden-mobile">
      <h2 class="subtitle">Which dance would you like to learn?</h2>
    </div>
    <div class="menu container padded">
      <div
        class="dance-card card is-clickable"
        v-for="dance in danceList"
        :key="dance.title"
        @mouseover="hover = dance.hovering = true"
        @mouseleave="hover = dance.hovering = false"
        @click="selectedDance = dance"
      >
        <div class="card-image">
          <figure class="image is-2by3">
            <img v-if="!dance.hovering" :src="dance.thumbnail" alt="" />
            <img v-if="dance.hovering" :src="dance.animatedThumb" alt="" />
          </figure>
        </div>
        <div class="card-content">
          {{ dance.title }}
        </div>
      </div>
    </div>

    <div v-bind:class="{ 'is-active': selectedDance }" class="modal">
      <div class="modal-background"></div>
      <div class="modal-content">
        <LessonCard
          v-bind:dance="selectedDance"
          v-on:closed="selectedDance = null"
          v-on:lesson-selected="danceLessonSelected"
        />
      </div>
    </div>
  </section>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';
import DanceEntry, { LessonSelection, dances } from '../../model/DanceEntry';
import LessonCard from '../elements/LessonCard.vue';

export default defineComponent({
  name: 'DanceMenu',
  components: {
    LessonCard,
  },
  setup(props, ctx) {
    const danceList = ref(dances);
    const selectedDance = ref(null as DanceEntry | null);

    function danceLessonSelected(sel: LessonSelection) {
      ctx.emit('dance-selected', sel);
      selectedDance.value = null;
    }

    return {
      selectedDance,
      danceList,
      danceLessonSelected,
    };
  },
});
</script>

<style lang="scss" scoped>
.menu {
  text-align: left;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  grid-gap: 0.5em;
}
.menu .card {
  display: block;
}
.dance-card {
  height: max-content;
  transition: transform 0.2s, box-shadow 0.2s;

  &:hover {
    box-shadow: 0 0.5em 1em -0.125em rgba(10, 10, 10, 0.3),
      0 0 0 2px rgba(10, 10, 10, 0.05);
    transform: scale(0.98);
  }
}

img {
  object-fit: fill;
}

.subtitle {
  margin: 2rem 1rem 2em;
  color: white;
}

.section {
  padding: 1.5rem;
}
</style>
