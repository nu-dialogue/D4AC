<template>
  <b-container class="d-flex flex-column">
    <header>
      <b-row>
        <h1>
          D4AC (Amazon Polly Speech Synthesizer)
          <b-button v-show="isShow" @click="startAmazon">Start Dialog</b-button>
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
    <footer>
      <audio src=""></audio>
    </footer>
  </b-container>
</template>
<script>
import SystemUtterance from "../components/SystemUtterance.vue";
import UserUtterance from "../components/UserUtterance.vue";
import UtteranceImage from "../components/UtteranceImage.vue";
import Mixin from "./dialogmixin.js";
import { CognitoIdentityClient } from "@aws-sdk/client-cognito-identity";
import { fromCognitoIdentityPool } from "@aws-sdk/credential-provider-cognito-identity";
import { Polly } from "@aws-sdk/client-polly";
import { getSynthesizeSpeechUrl } from "@aws-sdk/polly-request-presigner";
let client = undefined;

// Set the parameters
const speechParams = {
  OutputFormat: "mp3", // For example, 'mp3'
  SampleRate: "16000", // For example, '16000
  Text: "", // The 'speakText' function supplies this value
  TextType: "text", // For example, "text"
  VoiceId: "Takumi", // For example, "Matthew"
};

export default {
  name: "DialogMainAmazon",
  mixins: [Mixin],
  components: {
    SystemUtterance,
    UserUtterance,
    UtteranceImage,
  },
  beforeRouteLeave(to, from, next) {
    this.started = false;
    if (this.recog != undefined) this.recog.abort();
    next();
  },
  methods: {
    startAmazon: function () {
      client = new Polly({
        region: this.$store.state.pollyRegion,
        credentials: fromCognitoIdentityPool({
          client: new CognitoIdentityClient({ region: this.$store.state.pollyRegion }),
          identityPoolId: this.$store.state.pollyIdentityPoolId, // IDENTITY_POOL_ID
        }),
      });
      this.startWithRecognition(this.speechfuncAmazon);
    },
    speechfuncAmazon: async function (utterance) {
      console.log(`speechfuncAmazon ${utterance}`)
      speechParams.Text = utterance;
      try {
        let url = await getSynthesizeSpeechUrl({
          client,
          params: speechParams,
        });
        console.log(url);
        const audio = new Audio(url);
        //            audio.src = url;
        audio.autoplay = true;
        audio.addEventListener("ended", this.afterSpeech);
        audio.load();
        audio.play();
      } catch (err) {
        console.log("Error", err);
      }
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