import { ref } from 'vue';

class OptionsManager {

  public workflowId = ref(null as string | null);

  public participantId = ref(null as string | null);

  constructor() {
    this.parsePath();
    window.addEventListener('hashchange', this.parsePath);
  }

  parsePath() {
    const urlParams = new URLSearchParams(window.location.search);

    console.log('Parsing path....', urlParams);

    this.workflowId.value = urlParams.get('experimentId');
    this.participantId.value = urlParams.get('participantId');
  }
}

const optionsManager = new OptionsManager();
export default optionsManager;
