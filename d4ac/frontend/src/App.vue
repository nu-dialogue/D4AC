<template>
  <b-container fluid id="app" class="d-flex flex-column">
    <b-navbar variant="info" class="d-frex">
      <b-navbar-brand>D4AC</b-navbar-brand>
      <b-navbar-nav>
        <b-nav-item class="mr-4" to="/">Chrome Speech Synthesis</b-nav-item>
        <b-nav-item class="mr-4" to="/Amazon">Amazon Polly</b-nav-item>
        <b-nav-item class="mr-4" to="/Text">Text IO</b-nav-item>
      </b-navbar-nav>
    </b-navbar>
    <router-view />
  </b-container>
</template>
<script>
import axios from 'axios'
export default {
  name:"app",
  created(){
    axios.get("/config/").then((ret)=> {
      console.log(JSON.stringify(ret.data))
      this.$store.commit('setPeriod',ret.data.user_status.silence.period)
      this.$store.commit('setSilence',ret.data.user_status.silence.send)
      this.$store.commit('setSuEnd',ret.data.user_status.su_end.send)
      this.$store.commit('setUuEnd',ret.data.user_status.uu_end.send)
      this.$store.commit('setBotId',ret.data.dialog_server.botId)
      this.$store.commit('setInitTopicId',ret.data.dialog_server.initTopicId)
      this.$store.commit('setContinuousVoiceRecognition',ret.data.continuous_voice_recognition)
      this.$store.commit('setPollyIdentityPoolId',ret.data.amazon_polly.identityPoolId)
      this.$store.commit('setPollyRegion',ret.data.amazon_polly.region)
    })
  }
}
</script>
<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  min-height: 100vh;
  min-width: 90vw;
}

#nav {
  padding: 30px;
}

#nav a {
  font-weight: bold;
  color: #2c3e50;
}

#nav a.router-link-exact-active {
  color: #42b983;
}
</style>
