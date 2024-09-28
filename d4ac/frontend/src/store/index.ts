import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    botId: "aaaaa",
    initTopicId:"bbbbb",
    continuousVoiceRecognition: false,
    pollyIdentityPoolId:"",
    pollyRegion:"",
    silence: false,
    su_end: false,
    uu_end: false,
    period: 5.0
  },
  mutations: {
    setBotId(state,id){
      state.botId = id
    },
    setInitTopicId(state,id){
      state.initTopicId = id
    },
    setContinuousVoiceRecognition(state,continuous){
      state.continuousVoiceRecognition = continuous;
    },
    setPollyIdentityPoolId(state,id){
      state.pollyIdentityPoolId = id
    },
    setPollyRegion(state,region){
      state.pollyRegion = region
    },
    setSilence(state,enable){
      state.silence = enable
    },
    setPeriod(state,sec){
      state.period = sec
    },
    setSuEnd(state,suEnd){
      state.su_end = suEnd;
    },
    setUuEnd(state,uuEnd){
      state.uu_end = uuEnd;
    }

  },
  actions: {
  },
  modules: {
  }
})
