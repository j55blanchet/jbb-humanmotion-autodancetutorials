<template>
  <transition-group name="slide-fade" mode="out-in" tag="div" class="instructionCarousel">
    <p
      class="flextag"
      :class="[sizeClass, tagClass]"
      v-for="inst in instructions"
      :key="inst.id">{{inst.text}}</p>
  </transition-group>
</template>

<script lang="ts">

import { defineComponent } from 'vue';

export type Instruction = {
  id: number;
  text: string;
}

export default defineComponent({
  props: {
    instructions: {
      type: Array,
      default: Array,
    },
    sizeClass: {
      type: String,
      default: 'is-normal',
    },
    tagClass: {
      type: String,
      default: 'is-dark',
    },
  },
});
</script>

<style lang="scss">

.instructionCarousel {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-flow: row wrap;
  width: 100%;

  .flextag {
    border-radius: 0.25rem;
    text-align: center;
    border: 1px solid black;
    background: #EFEFEF;
    padding: 0.25rem 0.5rem;
  }

  .flextag.is-large {
    font-size: 2rem;
    border: 2px solid black;
    border-radius: 0.5rem;
  }

  .flextag.is-white {
    background: #EFEFEF;
  }
}

/* Enter and leave animations can use different */
/* durations and timing functions.              */
.slide-fade-enter-active {
  transition: all .15s ease;
  overflow: hidden;
  // transform: translateX(-100%);
}
.slide-fade-leave-active {
  transition: all .15s ease;
  overflow: clip;
  // transform: translateX(-100%);
}
.slide-fade-enter, .slide-fade-leave-to
/* .slide-fade-leave-active below version 2.1.8 */ {
  transform: translateX(10px) scaleX(0);
  opacity: 0;
}

</style>
