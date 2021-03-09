<template>
  <div class="onboardingUI">
    <div class="vcenter-parent">
      <div class="content">
        <h3>Here's how to use this app </h3>

        <span v-show="stage == 0">
          <p>Point forward with a flat hand to proceed</p>
          <span class="icon is-large" >
            <i class="fas fa-2x fa-hand-paper fa-rotate-90"></i>
          </span>
        </span>

        <span v-show="stage == 1">
          <p>Point to the left with a flat hand to go backwards</p>
          <span class="icon is-large fa-flip-horizontal" v-show="stage == 1">
            <i class="fas fa-2x fa-hand-paper fa-rotate-90"></i>
          </span>
        </span>

      </div>
    </div>
  </div>
</template>

<script lang="ts">

import {
  defineComponent, ref, onMounted, onBeforeUnmount,
} from 'vue';

import eventHub, { EventNames, Gestures } from '../services/EventHub';

const OnboardingStage = {
  TrySelectNext: 0,
  TrySelectPrevious: 1,
};

export default defineComponent({
  name: 'OnboardingUI',
  setup() {
    const stage = ref(OnboardingStage.TrySelectNext);
    const output = ref('');

    const onGesture = (gesture: string) => {
      output.value = gesture;

      if (stage.value === OnboardingStage.TrySelectNext && gesture === Gestures.pointRight) {
        stage.value = OnboardingStage.TrySelectPrevious;
      }
    };

    onMounted(() => {
      eventHub.on(EventNames.gesture, onGesture);
    });
    onBeforeUnmount(() => {
      eventHub.off(EventNames.gesture, onGesture);
    });

    return {
      stage,
      output,
    };
  },
});
</script>

<style lang="scss">

.onboardingUI {
  width: 100%;
  height: 100%;
}

</style>
