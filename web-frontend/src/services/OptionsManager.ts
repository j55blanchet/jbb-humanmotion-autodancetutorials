import { ref } from 'vue';

class OptionsManager {

  public workflowId = ref(null as string | null);

  public participantId = ref(null as string | null);

  public participantIdWasSet = ref(false);

  public isTest = ref(false);

  constructor() {
    this.parsePath();
    window.addEventListener('hashchange', this.parsePath);
  }

  parsePath() {
    const urlParams = new URLSearchParams(window.location.search);

    console.log('Parsing path....', urlParams);

    this.workflowId.value = urlParams.get('workflowId');
    this.participantId.value = urlParams.get('participantId');
    this.isTest.value = this.workflowId.value === null || this.participantId.value === null;

    if (this.participantId.value) {
      this.participantIdWasSet.value = true;
    }
  }
}

const optionsManager = new OptionsManager();
export default optionsManager;
