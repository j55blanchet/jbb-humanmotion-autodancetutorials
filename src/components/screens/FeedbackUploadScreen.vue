<template>
  <section class="section">
    <div class="container">
      <h1 class="title">{{title}}</h1>
      <h2 class="subtitle" v-show="subtitle">{{subtitle}}</h2>

      <p class="block"><strong>Instructions:</strong> {{prompt}}</p>

      <div class="block" v-if="state === 'Record'">
        <WebcamBox />

        <div class="field is-grouped is-grouped-centered" v-show="webcamStatus === 'running'">
          <p class="control">
            <span class="record-icon" :class="{'is-recording': isRecording}">
            </span>
            <!-- <span class="icon is-medium" :class="{'has-text-danger': isRecording}">
              <FAIcon icon="record-vinyl" size="lg" pulse />
            </span> -->
          </p>
          <p class="control">
            <button class="button animate-width"
              @click="toggleRecording">

               <span v-show="isRecording">
                Stop
              </span>
              <span v-show="!isRecording">
                Record
              </span>

              <!-- <span v-if="!isRecording">Start Recording</span> -->
            </button>
          </p>
        </div>
      </div>
      <video class="block flipped" v-else controls :src="recordedObjectUrl"></video>
      <div class="block" v-if="state === 'Review'">
        <div class="field is-grouped is-grouped-centered">
          <p class="control">
            <button class="button" :disabled="isUploading" @click="rerecord">
              Rerecord
              <!-- <span class="icon is-medium" :class="{'has-text-danger': isRecording}">
                <FAIcon icon="record-vinyl" />
              </span> -->
              <!-- <span v-if="!isRecording">Start Recording</span> -->
            </button>
          </p>
          <p class="control">
            <button class="button is-primary"
              :disabled="isUploading"
              :class="{'is-loading': isUploading}"
              @click="uploadVideo">
              Upload Video
            </button>
          </p>
        </div>

        <div class="notification" v-if="uploadError">
          <strong>Error Uploading Video:</strong>
          {{uploadError}}
        </div>
      </div>
      <div class="block has-text-centered" v-if="state === 'Success'">
        <span class="icon"><i class="fas fa-check"></i></span> Upload Successful
      </div>

      <div class="block buttons is-right" >
        <!-- {{successfullyUploaded}} -->
        <button v-show="!successfullyUploaded" class="is-outlined button is-danger" @click="$emit('upload-canceled')">Cancel</button>
        <button :disabled="!successfullyUploaded" class="button is-primary" @click="$emit('upload-completed')">Done</button>
      </div>

    </div>
  </section>
</template>

<script lang="ts">
import { computed, defineComponent, ref } from 'vue';
import webcamProvider from '@/services/WebcamProvider';
import AzureUploader from '@/services/AzureUploader';
import WebcamBox from '@/components/elements/WebcamBox.vue';

export default defineComponent({
  name: 'UploadScreen',
  components: { WebcamBox },
  emits: ['upload-canceled', 'upload-completed'],
  props: {
    title: {
      type: String,
      default: 'Video Upload',
    },
    subtitle: {
      type: String,
      default: null,
    },
    prompt: {
      type: String,
      default: 'Upload your video here',
    },
    uploadFilename: {
      type: String,
      default: null,
    },
  },
  setup() {

    const state = ref('Record' as 'Record' | 'Review' | 'Success');

    const lastRecordedBlob = ref(null as Blob | null);
    const recordedObjectUrl = ref('');
    const isUploading = ref(false);
    const uploadError = ref(null as null | any);
    const successfullyUploaded = computed(() => state.value === 'Success');

    return {
      state,
      webcamProvider,
      webcamStatus: webcamProvider.webcamStatus,
      isRecording: webcamProvider.isRecording,
      lastRecordedBlob,
      recordedObjectUrl,
      isUploading,
      uploadError,
      successfullyUploaded,
    };
  },
  methods: {
    async toggleRecording() {
      if (!webcamProvider.isRecording.value) {
        await webcamProvider.startWebcam();
        await webcamProvider.startRecording();
      } else {
        this.lastRecordedBlob = await webcamProvider.stopRecording();
        this.recordedObjectUrl = URL.createObjectURL(this.lastRecordedBlob);
        this.state = 'Review';
        await webcamProvider.stopWebcam();
      }
    },
    async rerecord() {
      this.successfullyUploaded = false;
      this.lastRecordedBlob = null;
      this.recordedObjectUrl = '';
      this.uploadError = null;
      this.state = 'Record';
      await webcamProvider.startWebcam();
    },
    async uploadVideo() {
      if (!this.lastRecordedBlob) return;
      if (this.isUploading) return;

      this.isUploading = true;
      this.uploadError = null;
      const blobName = `${this.$props.uploadFilename}.webm`;

      try {
        await AzureUploader.upload(this.lastRecordedBlob, blobName);
      } catch (e) {
        console.error('Error uploading video', e);
        this.uploadError = e;
      }

      if (this.uploadError === null) {
        this.state = 'Success';
      }

      this.isUploading = false;
    },
  },
});

</script>

<style lang="scss">

@import "@/assets/main.scss";

.animate-width {
  transition: width 0.2s ease;
}

.record-icon {
  display: block;
  width: 1.5rem;
  height: 1.5rem;
  border-radius: 1rem;
  background-color: $dark;
  transition: background-color 0.2s ease;

  &.is-recording {
    background-color: $red;
  }
}

.control .record-icon {
  margin-top: 8px;
}
</style>
