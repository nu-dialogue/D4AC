<template>
  <b-container class="d-flex flex-column">
    <header>
      <b-row>
        <h1>
          D4AC (with Chrome Speech Synthesis)

          <b-button v-show="isShow" @click="startGoogle">Start Dialog</b-button>
          <b-icon
            v-show="voice"
            icon="chat-dots"
            scale="2"
            animation="throb"
          ></b-icon>
          {{ userutterance }} {{status}}
        </h1>
      </b-row>
    </header>
    <article>
      <component
        v-for="utterance in utterances"
        v-bind:is="utterance.component"
        v-bind:key="utterance"
        :utterance="utterance.utterance"
      />
    </article>
  </b-container>
</template>
<script>
import SystemUtterance from "../components/SystemUtterance.vue";
import UserUtterance from "../components/UserUtterance.vue";
import UtteranceImage from "../components/UtteranceImage.vue"
import Mixin from "./dialogmixin.js";
export default {
  name: "DialogMainGoogle",
  mixins: [Mixin],
  components: {
    SystemUtterance,
    UserUtterance,
    UtteranceImage
  },
  beforeRouteLeave(to, from, next) {
    this.started = false
    if (this.recog != undefined) this.recog.abort();
    next();
  },
  methods: {
    startGoogle: function () {
      this.startWithRecognition(this.speechfuncGoogle);
    },
    speechfuncGoogle: async function (utterance) {
      console.log(`speechfuncGoogle ${utterance}`);
      const uttr = new SpeechSynthesisUtterance();
      uttr.text = utterance;
      uttr.addEventListener("start", () => {
        console.log("start system voice");
        this.isSystem = true;
        //if (!this.continuous) this.recog.stop();
      });

      uttr.addEventListener("end", this.afterSpeech);
      window.speechSynthesis.cancel();
      window.speechSynthesis.speak(uttr);
    },
  },
};
</script>
<style scoped>
.container {
  flex-grow: 1;
  overflow-y: auto;
  overflow-x: hidden;
}
header {
  flex-basis: 50px;
}
article {
  flex-grow: 1;
  overflow-y: auto;
  overflow-x: hidden;
}
</style>