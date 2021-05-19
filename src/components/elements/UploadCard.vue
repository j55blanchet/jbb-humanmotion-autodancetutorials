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
        v-if="isInitial || isSaving"
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
                  filesChange($event.target.name, $event.target.files);
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
            </div>
          </div>
        </div>
      </form>
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
      default: 'Upload your file here',
    },
    savingText: {
      type: String,
      default: 'Processing File...',
    },
    onFileSelected: {
      type: Function,
      default: () => {},
    },
  },
  data() {
    return {
      uploadedFiles: [],
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
      this.uploadedFiles = [];
      this.uploadError = null;
    },
    async save(formData: FormData) {
      // upload data to the server
      this.currentStatus = Status.Saving;

      const result = await this.onFileSelected();
      if (result) this.$emit('done');
      // else

      // upload(formData)
      //   .then(x => {
      //     this.uploadedFiles = [].concat(x);
      //     this.currentStatus = Status.Success;
      //   })
      //   .catch(err => {
      //     this.uploadError = err.response;
      //     this.currentStatus = Status.Failed;
      //   });
    },
    filesChange(fieldName: string, fileList: Array<any>) {
      // handle file changes
      const formData = new FormData();

      if (!fileList.length) return;

      // append the files to FormData
      Array
        .from(Array(fileList.length).keys())
        .forEach((x) => {
          formData.append(fieldName, fileList[x], fileList[x].name);
        });

      // save it
      this.save(formData);
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
