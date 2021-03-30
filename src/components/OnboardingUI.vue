<template>
  <div class="onboardingUI">
    <div class="overlay instructions-overlay mb-4">
       <InstructionCarousel :instructions="instructions" class="m-2"/>
       <InstructionCarousel v-show="stage !== OnboardingStage.done" :instructions="[{id: 0, text: 'How to use this app'}]" class="m-2"/>
    </div>
    <div class="vcenter-parent" v-show="stage !== OnboardingStage.done">
      <div class="content translucent-text is-rounded p-6">
        <!-- <h3 class="has-text-white">Here's how to use this app</h3> -->


        <span v-show="stage == 0">
          <span class="icon is-large" >
            <i class="fas fa-2x fa-hand-paper fa-rotate-90"></i>
          </span>
        </span>

        <span v-show="stage == 1">
          <!-- <p>Point to the left with a flat hand to go backwards</p> -->
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
  computed,
  defineComponent, onBeforeUnmount, onMounted, ref,
} from 'vue';

import { setupGestureListening, GestureNames, TrackingActions } from '../services/EventHub';
import InstructionCarousel, { Instruction } from './elements/InstructionCarousel.vue';

const OnboardingStage = {
  trySelectNext: 0,
  trySelectPrevious: 1,
  done: 2,
};

export default defineComponent({
  name: 'OnboardingUI',
  components: { InstructionCarousel },
  setup(props, ctx) {
    const stage = ref(OnboardingStage.trySelectNext);
    const output = ref('');

    const instructions = computed(() => {
      const instructs: Instruction[] = [];
      if (stage.value === OnboardingStage.trySelectNext) {
        instructs.push({
          id: 0,
          text: 'Point to the right with a flat hand to proceed',
        });
      } else if (stage.value === OnboardingStage.trySelectPrevious) {
        instructs.push({
          id: 1,
          text: 'Point to the left with a flat hand to repeat an activity',
        });
      } else {
        instructs.push({
          id: 2,
          text: 'You got it!',
        });
      }
      return instructs;
    });

    onMounted(() => {
      TrackingActions.requestTracking('onboarding');
    });
    onBeforeUnmount(() => {
      TrackingActions.endTrackingRequest('onboarding');
    });

    setupGestureListening({
      [GestureNames.pointRight]: () => {
        if (stage.value === OnboardingStage.trySelectNext) {
          stage.value = OnboardingStage.trySelectPrevious;
        }
      },
      [GestureNames.pointLeft]: () => {
        if (stage.value === OnboardingStage.trySelectPrevious) {
          stage.value = OnboardingStage.done;
          TrackingActions.endTrackingRequest('onboarding');
          setTimeout(() => {
            ctx.emit('onboarding-complete');
          }, 1500);
        }
      },
    });

    return {
      stage,
      output,
      instructions,
      OnboardingStage,
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
