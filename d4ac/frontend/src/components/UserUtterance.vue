<template>
  <b-row align-h="start">
    <b-col cols="11" class="user"
      ><b-avatar variant="success"></b-avatar>{{ utterance }}</b-col
    >
  </b-row>
</template>
<script>
export default {
  name: "UserUtterance",
  props: {
    utterance: String,
    expression: String,
  },
};
</script>
<style scoped>
.user {
  text-align: left;
  background-color: aqua;
  border-radius: 10px;
  margin: 10px;
  padding: 10px;
}
</style>