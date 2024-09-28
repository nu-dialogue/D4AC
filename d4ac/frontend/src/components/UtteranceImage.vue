<template>
    <b-row align-h="end"><b-col cols="2">      <b-img thumbnail 
    v-bind:src="imgSrc" rounded>

    </b-col>
</b-row>
</template>
<script>
export default {
  name: "UtteranceImage",
  props: {
    expression: String,
    utterance: String,
  },
  computed: {
    imgSrc: function () {
      return "/static/images/" + this.utterance;
    },
  },
  created() {
    console.log("created  Image");
  },
};
//    width="256" height="256"
</script>