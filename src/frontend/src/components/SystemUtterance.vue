<template>
  <b-row align-h="end">
    <b-col cols="11" class="system">
      {{ utterance }}<b-avatar variant="primary"></b-avatar>
    </b-col>
  </b-row>
</template>
<script>
export default {
  name: "SystemUtterance",
  props: {
    expression: String,
    utterance: String,
  },
  created() {
    console.log("created system");
  },
};
</script>
<style scoped>
.system {
  text-align: right;
  background-color: darkseagreen;
  border-radius: 10px;
  margin: 10px;
  padding: 10px;
}
</style>