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
  defineComponent, ref,
} from 'vue';

import { setupGestureListening, GestureNames, TrackingActions } from '../services/EventHub';

const OnboardingStage = {
  TrySelectNext: 0,
  TrySelectPrevious: 1,
  Done: 2,
};

export default defineComponent({
  name: 'OnboardingUI',
  setup(props, ctx) {
    const stage = ref(OnboardingStage.TrySelectNext);
    const output = ref('');

    setupGestureListening({
      [GestureNames.pointRight]: () => {
        if (stage.value === OnboardingStage.TrySelectNext) {
          stage.value = OnboardingStage.TrySelectPrevious;
        }
      },
      [GestureNames.pointLeft]: () => {
        if (stage.value === OnboardingStage.TrySelectPrevious) {
          stage.value = OnboardingStage.Done;
          ctx.emit('onboarding-complete');
          TrackingActions.endTrackingRequest();
        }
      },
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

  .content {
    color: black !important;
    backdrop-filter: blur(4px);
    background: rgba(255, 255, 255, 0.4);
    border-radius: 1rem;
    padding: 1rem;
  }

}

</style>
