<template>
  <div class="card upload-card">
    <div class="card-header">
      <h4 class="card-header-title">Upload File</h4>

      <a class="card-header-icon" @click="$emit('cancelled')">
        <i class="fas fa-times"></i>
      </a>
    </div>
    <div class="card-content">
      <form
        enctype="multipart/form-data"
        novalidate
        v-if="isInitial || isSaving || isFailed"
      >
        <div class="field">
        </div>
        <div class="field">
          <div class="control">
            <div class="dropbox is-rounded">
              <input
                type="file"
                :name="uploadFieldName"
                :disabled="isSaving"
                @change="
                  save($event.target.files, $event.target);
                  fileCount = $event.target.files.length;
                "
                :accept="uploadAccept"
                class="file-input"
              />
              <p class="is-size-7" v-if="isInitial">
                {{uploadInstructions}}
              </p>
              <p class="is-size-7" v-if="isSaving">
                {{savingText}}
              </p>
              <div class="is-size-7 has-text-centered" v-if="isFailed">
                <p>Error saving:</p>
                <p style="max-width:60ch;" class="has-text-danger">{{uploadError}}</p>
                <p><strong>Please try again.</strong></p>
              </div>
            </div>
          </div>
        </div>
      </form>
      <div class="has-text-success" v-if="isSuccess">{{successText}}</div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

const Status = Object.freeze({
  Initial: 'Initial',
  Saving: 'Saving',
  Success: 'Success',
  Failed: 'Failed',
});

export default defineComponent({
  name: 'UploadCard',
  props: {
    uploadAccept: {
      type: String,
      default: '*',
    },
    uploadInstructions: {
      type: String,
      default: 'Click here or drag your file(s) over this area',
    },
    savingText: {
      type: String,
      default: 'Processing File(s)...',
    },
    onFilesSelected: {
      type: Function,
      default: () => {},
    },
    successText: {
      type: String,
      default: 'Files uploaded successfully',
    },
  },
  data() {
    return {
      uploadError: null,
      currentStatus: null as null | string,
      uploadFieldName: 'files',
    };
  },
  emits: ['cancelled', 'done'],
  computed: {
    isInitial() { return (this as any).currentStatus === Status.Initial; },
    isSaving() { return (this as any).currentStatus === Status.Saving; },
    isSuccess() { return (this as any).currentStatus === Status.Success; },
    isFailed() { return (this as any).currentStatus === Status.Failed; },
  },
  methods: {
    reset() {
      // reset form to initial state
      this.currentStatus = Status.Initial;
      this.uploadError = null;
    },
    async save(fileList: FileList) {
      // upload data to the server
      this.currentStatus = Status.Saving;

      try {
        const result = await this.onFilesSelected(fileList);
        if (result) {
          this.$emit('done');
          this.currentStatus = Status.Success;
        } else {
          this.currentStatus = Status.Initial;
        }
      } catch (e) {
        this.currentStatus = Status.Failed;
        this.uploadError = e;
      }
    },
  },
  mounted() {
    this.reset();
  },
});
</script>

<style lang="scss">
.upload-card {
  .file-input {
    opacity: 0;
    width: 100%;
    height: 160px;
    position: absolute;
    cursor: pointer;
  }

  .dropbox {
    outline: 2px dashed gray;
    outline-offset: -1rem;
    min-height: 160px;
    min-width: 320px;
    color: dimgray;
    padding: 1.5rem;
    position: relative;
    cursor: pointer;

    &:hover {
      background: lightblue;
    }
  }
}
</style>
