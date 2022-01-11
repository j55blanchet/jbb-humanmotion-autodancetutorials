<template>
   <div class="webcam-prompt-card vcenter-parent" >
        <div class="card">
          <div class="card-header">
            <h3 class="card-header-title">
            Webcam Access Needed
            </h3>
          </div>
          <div class="card-content">
            <div class="content">
              <p>
                During the lesson, you'll step back from your computer
                and control this app with gestures. Later on, we'll also
                use your webcam to give you tips on your technique.
              </p>
              <p class="notification is-warning">
                Please <strong>stop other programs that are using your webcam</strong>. On most computers, only one app is able to use the webcam at a time.
              </p>
              <p>
                <strong>To continue, please grant access to your webcam.</strong>
              </p>
            </div>
          </div>
          <div class="card-content">
            <div class="buttons is-right">
              <a @click="$emit('cancelSelected')" class="is-inverted button is-danger">
                Cancel
              </a>
              <a @click="$emit('startWebcamSelected')" class="button is-primary">
                Start Webcam
              </a>
            </div>
          </div>
        </div>
      </div>
</template>

<script>

import { defineComponent } from 'vue';

export default defineComponent({
  name: 'WebcamPromptCard',
});
</script>

<style lang="scss">

.webcam-prompt-card .content {
  max-width: 60ch;
  text-align: left;
}
</style>
