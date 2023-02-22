<template>
<div class="box m-4 hover-expand is-clickable"
      :key="workflow.id">
      <div class="level">
        <div class="level-item mr-4" v-if="workflow.thumbnailSrc">
          <img :src="workflow.thumbnailSrc" class="image is-96x96 is-cover">
        </div>
        <div class="level-item has-text-left">
          <div>
            <p class="is-uppercase">{{workflow.title}}</p>
            <p class="is-size-7 has-text-grey mt-1 mb-1" style="max-width:40ch;"><strong>Algorithm: </strong>{{workflow.creationMethod}}</p>
            <p class="is-size-7 has-text-grey mt-1 mb-1" style="max-width:40ch;"><strong>Lesson: </strong>{{workflow.learningScheme}}</p>
            <p class="is-size-7 has-text-grey" v-if="isDebug"><strong>Created:</strong> {{workflow.created.toLocaleDateString()}} at {{workflow.created.toLocaleTimeString()}}</p>
          </div>
        </div>
      </div>
      <div style="" class="is-size-7" v-if="isDebug">
        <button class="button is-info is-light" @click.stop="copyLink(workflow.id, $event)">Copy Link</button>
      </div>
    </div>
</template>

<script lang="ts">

import { computed, defineComponent, ref } from 'vue';
import { Workflow } from '@/model/Workflow';
import optionsManager from '@/services/OptionsManager';

function copyLink(id: string, event: Event) {
  const url = `${window.location.protocol}://${window.location.host}?workflowId=${id}&participantId=PARTICIPANTID`;
  navigator.clipboard.writeText(url);

  const target = event?.target as (HTMLButtonElement | undefined);
  if (target) {
    target.classList.add('is-success');
    const originalText = target.innerText;
    target.innerText = 'Copied!';
    target.disabled = true;

    setTimeout(() => {
      if (target) {
        target.classList.remove('is-success');
        target.innerText = originalText;
        target.disabled = false;
      }
    }, 1000);
  }
}

export default defineComponent({
  name: 'MainMenuWorkflowCard',
  emits: ['workflow-selected'],
  props: {
    workflow: {
      type: Object as () => Workflow,
      required: true,
    },
  },
  setup(props, ctx) {
    return {
      isDebug: optionsManager.isDebug,
      copyLink,
    };
  },
});

</script>
