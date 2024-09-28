<template>
  <b-container class="d-flex flex-column">
    <header>
      <b-row>
        <h1>
          D4AC (Text Input/Output)
          <b-button v-show="isShow" @click="start">Start Dialog</b-button>
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
      <b-form inline v-if="started">
        <b-form-input
          id="input-1"
          class="mb-8"
          v-model="input_text"
          placeholder="text input"
        ></b-form-input
        ><b-button @click="textinput">Text Input</b-button>
      </b-form>
    </footer>
  </b-container>
</template>
<script>
import SystemUtterance from "../components/SystemUtterance.vue";
import UserUtterance from "../components/UserUtterance.vue";
import UtteranceImage from "../components/UtteranceImage.vue"
import Mixin from "./dialogmixin.js";
export default {
  name: "DialogMainText",
  mixins: [Mixin],
  data() {
    return {
      input_text: "",
    };
  },
  components: {
    SystemUtterance,
    UserUtterance,
    UtteranceImage
  },
    beforeRouteLeave(to, from, next) {
    this.started = false
    next();
  },
  methods: {
    textinput: function () {
      this.utterances.unshift({
        component: "UserUtterance",
        expression: this.input_text,
        utterance: this.input_text,
      });
      this.send(this.input_text);
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
footer {
  display: flex;
  flex-basis: 200px;
}
</style>