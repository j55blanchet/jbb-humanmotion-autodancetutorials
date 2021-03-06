<template>
  <div class="onboardingUI">
    <div class="overlay instructions-overlay mb-4">
       <InstructionCarousel :instructions="instructions" class=""/>
       <!-- <InstructionCarousel v-show="stage !== OnboardingStage.done" :instructions="[{id: 0, text: 'How to use this app'}]" class="m-2"/> -->
    </div>
    <div class="vcenter-parent" v-show="stage !== OnboardingStage.done">
      <div class="content translucent-text is-rounded p-6">
        <GestureIcon :gesture="gestureIcon" />
      </div>
    </div>
    <div class="overlay overlay-top overlay-right mt-4 mr-4" v-show="stage !== OnboardingStage.done">
      <button class="button" @click="skipOnboarding">Skip</button>
    </div>
  </div>
</template>

<script lang="ts">

import { usingHolistic } from '@/services/MediaPipe';
import {
  computed,
  defineComponent, onBeforeUnmount, onMounted, ref,
} from 'vue';

import { setupGestureListening, GestureNames, TrackingActions } from '../services/EventHub';
import InstructionCarousel, { Instruction } from './elements/InstructionCarousel.vue';
import GestureIcon, { GestureIcons } from './elements/GestureIcon.vue';

const OnboardingStage = {
  trySelectNext: 0,
  trySelectPrevious: 1,
  tryPerformPlay: 2,
  done: 3,
};

export default defineComponent({
  name: 'OnboardingUI',
  components: { InstructionCarousel, GestureIcon },
  setup(props, ctx) {
    const stage = ref(OnboardingStage.trySelectNext);
    const output = ref('');

    const instructions = computed(() => {
      const instructs: Instruction[] = [];
      if (stage.value === OnboardingStage.trySelectNext) {
        instructs.push({
          id: 0,
          text:
            usingHolistic
              ? 'Point to the right with a flat hand to proceed'
              : 'Point your left forearm to the right to proceed',
        });
      } else if (stage.value === OnboardingStage.trySelectPrevious) {
        instructs.push({
          id: 1,
          text:
          usingHolistic
            ? 'Point to the left with a flat hand to repeat an activity'
            : 'Point your right forearm to the left to repeat an activity',
        });
      } else if (stage.value === OnboardingStage.tryPerformPlay) {
        instructs.push({
          id: 2,
          text: 'Put your hands together in a Namaste greeting to play a video',
        });
      } else {
        instructs.push({
          id: 3,
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

    function advanceStage() {
      if (stage.value === OnboardingStage.trySelectNext) {
        stage.value = OnboardingStage.trySelectPrevious;
      } else if (stage.value === OnboardingStage.trySelectPrevious) {
        stage.value = OnboardingStage.tryPerformPlay;
      } else if (stage.value === OnboardingStage.tryPerformPlay) {
        stage.value = OnboardingStage.done;
        TrackingActions.endTrackingRequest('onboarding');
        setTimeout(() => {
          ctx.emit('onboarding-complete');
        }, 1500);
      }
    }
    setupGestureListening({
      [GestureNames.pointRight]: () => {
        if (stage.value === OnboardingStage.trySelectNext) {
          advanceStage();
        }
      },
      [GestureNames.pointLeft]: () => {
        if (stage.value === OnboardingStage.trySelectPrevious) {
          advanceStage();
        }
      },
      [GestureNames.namaste]: () => {
        if (stage.value === OnboardingStage.tryPerformPlay) {
          advanceStage();
        }
      },
    });

    function skipOnboarding() {
      advanceStage();
    }

    const gestureIcon = computed(() => {
      switch (stage.value) {
        case OnboardingStage.trySelectNext:
          return GestureIcons.forward;
        case OnboardingStage.trySelectPrevious:
          return GestureIcons.backward;
        case OnboardingStage.tryPerformPlay:
          return GestureIcons.play;
        default:
          return '';
      }
    });

    return {
      stage,
      output,
      instructions,
      OnboardingStage,
      skipOnboarding,
      gestureIcon,
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
