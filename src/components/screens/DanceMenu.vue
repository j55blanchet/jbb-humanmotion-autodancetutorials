<template>
  <section class="section dance-menu">
    <div class="container content has-text-centered is-hidden-mobile">
      <h2 class="subtitle">Which dance would you like to learn?</h2>
    </div>
    <div class="menu container padded">
      <div
        class="dance-card card is-clickable shrink-hover"
        v-for="dance in motionList"
        :key="dance.title"
        @mouseover="hover = dance.hovering = true"
        @mouseleave="hover = dance.hovering = false"
        @click="selectedDance = dance"
      >
        <div class="card-image">
          <figure class="image is-2by3">
            <video :src="dance.videoSrc" />
          </figure>
        </div>
        <div class="card-content">
          {{ dance.title }}
        </div>
      </div>

      <div class="form-upload p-4">
        <h4 class="title is-4">Other Actions</h4>
        <div class="field">
          <div class="control is-expanded shrink-hover">
            <button class="button is-fullwidth" @click="uploadUIActive = true">Upload Custom Lesson</button>
          </div>
        </div>
        <div class="field">
          <div class="control is-expanded shrink-hover">
            <button class="button is-fullwidth" @click="$emit('pose-drawer-selected')">Pose Drawer Test</button>
          </div>
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

    <div v-bind:class="{ 'is-active': uploadUIActive }" class="modal">
      <div class="modal-background"></div>
      <div class="modal-content">
        <UploadCard
          @cancelled="uploadUIActive = false"
        />
      </div>
    </div>
  </section>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';
import DanceEntry, { LessonSelection } from '../../model/DanceEntry';
import LessonCard from '../elements/LessonCard.vue';
import UploadCard from '../elements/UploadCard.vue';
import motions from '../../services/MotionDatabase';

export default defineComponent({
  name: 'DanceMenu',
  emits: ['dance-selected', 'pose-drawer-selected'],
  components: {
    LessonCard,
    UploadCard,
  },
  setup(props, ctx) {
    const motionList = ref(motions);
    const selectedDance = ref(null as DanceEntry | null);
    const uploadUIActive = ref(false);

    function danceLessonSelected(sel: LessonSelection) {
      ctx.emit('dance-selected', sel);
      selectedDance.value = null;
    }

    return {
      selectedDance,
      motionList,
      danceLessonSelected,
      uploadUIActive,
    };
  },
});
</script>

<style lang="scss">

// .dance-menu {
  // backdrop-filter: blur(4px);
  // background: rgba(0, 0, 0, 0.2);
// }

.dance-menu {

  .menu {
    text-align: left;
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(210px, 1fr));
    grid-gap: 0.5em;
  }
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

  .shrink-hover {
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
