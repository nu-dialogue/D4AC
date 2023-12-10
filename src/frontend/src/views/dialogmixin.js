import axios from "axios";
export default {
    data() {
        return {
            sessionId: "",
            started: false,
            first: true,
            voice: false,
            recog: undefined,
            speechFunc: undefined,
            utterances: [],
            status: "",
            interval: undefined,
        }
    },
    computed: {
        isShow: function () {
            return (!this.voice);
        },
    },
    methods: {
        send: async function (utterance) {
            try {
                if (this.first) {
                    const ret = await axios.get(`/continuefirst/${this.sessionId}/${utterance}`);
                    console.log('/continuefirst/', ret)
                    this.first = false
                    await this.system(ret.data.systemUtterance);
                } else {
                    const ret = await axios.get(`/continue/${this.sessionId}/${utterance}`);
                    console.log('/continuefirst/', ret)
                    await this.system(ret.data.systemUtterance);
                }

            } catch (e) {
                this.status = "D4AC Error"
            }
        },
        start: async function () {
            if (!this.started) {
                await this.sendStart("start");
                this.started = true;
            }
        },
        startWithRecognition: async function (speechFunc) {
            this.speechFunc = speechFunc
            if (!this.started) {
                console.log("sendStart")
                await this.sendStart("start");
                this.started = true;
                const speechRecognition =
                    window.webkitSpeechRecognition || window.SpeechRecognition;
                const recog = new speechRecognition();
                recog.interimResults = true;
                recog.continuous = true;
                recog.onresult = async (event) => {
                    console.log("speech recognition onresult");
                    if (this.interval != undefined) {
                        console.log('cancel send userstatus')
                        clearInterval(this.interval)
                        this.interval = undefined
                    }
                    const length = event.results.length;
                    this.userutterance = event.results[length - 1][0].transcript;
                    if (event.results[length - 1].isFinal) {
                        this.utterances.unshift({
                            component: "UserUtterance",
                            expression: this.userutterance,
                            utterance: this.userutterance,
                        });
                        if (!this.$store.state.continuousVoiceRecognition) {
                            console.log("recog abort")
                            this.recog.abort();
                        }
                        //send message
                        await this.send(this.userutterance);
                    }
                };
                recog.onaudiostart = async () => {
                    console.log("recog start audio");
                    this.voice = true;
                };
                recog.onaudioend = async () => {
                    console.log("recog stop audio");
                    this.voice = false;
                };
                recog.onend = async () => {
                    console.log("recog onend");
                    if (this.$store.state.continuousVoiceRecognition && this.started) {
                        console.log("restarting recog");
                        this.recog.start();
                    } else {
                        console.log("no restarting recog");
                        this.voice = false
                    }
                };
                recog.nomatch = async () => {
                    console.log("recog not match")
                    this.voice = false
                }
                this.recog = recog;
                if (this.$store.state.continuousVoiceRecognition) this.recog.start()

            } else {
                console.log("voice recognition start manually")
                this.recog.start()
            }

        },
        sendStart: async function (utterance) {
            try {
                const ret = await axios.get(`/start/${utterance}`);
                console.log(ret);
                this.sessionId = ret.data.sessionId;
                await this.system(ret.data.systemUtterance);
            } catch (e) {
                this.status = "D4AC Error"
            }
        },
        afterSpeech: async function () {
            if (this.$store.state.su_end) {
                await this.sendEngagement();
            }
            //自動ユーザーステータス送信
            if (this.$store.state.silence) {
                const timing = this.$store.state.period * 1000
                console.log('start send userstatus', timing)
                if (this.interval != undefined) clearInterval(this.interval)
                this.interval = setInterval(async () => {
                    //if(this.recog!= undefined)this.recog.abort()
                    const ret = await axios.get(`/userstatus/${this.sessionId}`);
                    console.log('userstatus', ret)
                    if (ret.data != null && ret.data.systemUtterance != undefined) {
                        this.system(ret.data.systemUtterance)
                    }
                }, timing)
            }
            if (!this.$store.state.continuousVoiceRecognition) {

                try {
                    this.recog.start();

                } catch (e) {
                    console.log(e)
                }

            }
        },
        sendEngagement: async function () {
            this.isSystem = false;
            if (this.sessionId != "") {
                try {
                    const ret = await axios.get(`/engagement/${this.sessionId}`);
                    console.log(ret);
                    if (ret.data != null && ret.data.systemUtterance != undefined)
                        this.system(ret.data.systemUtterance);
                } catch (e) {
                    this.status = "D4ACエラー"
                }
            }


        },

        stop: function () {
            if (this.recog != null) this.recog.stop();
            this.recog = null;
        },
        system: async function (utterance) {
            const ut = utterance.utterance
            if (ut != "") {

                const reg = /\(.*?\)/
                const match = ut.match(reg)
                if (match != null) {
                    const reg2 = /^.*?\(/
                    const newutt = ut.match(reg2)
                    const str = match[0]
                    const image = str.substring(1, str.length - 1)
                    const str2 = newutt[0]
                    const u = str2.substring(0, str2.length - 1)
                    console.log(`utter ${image} ${u}`)
                    this.utterances.unshift({
                        component: "SystemUtterance",
                        expression: u,
                        utterance: u,
                    });
                    this.utterances.unshift({
                        component: "UtteranceImage",
                        expression: image,
                        utterance: image
                    })


                    if (this.speechFunc != undefined) {
                        if (!this.$store.state.continuousVoiceRecognition) {
                            console.log("recog abort")
                            if (this.recog != undefined) this.recog.abort()
                        }
                        if (this.interval != undefined) {
                            console.log('cancel send userstatus')
                            clearInterval(this.interval)
                            this.interval = undefined
                        }
                        this.speechFunc(u)
                    }
                } else {
                    this.utterances.unshift({
                        component: "SystemUtterance",
                        expression: ut,
                        utterance: ut,
                    });

                    if (this.speechFunc != undefined) {
                        if (!this.$store.state.continuousVoiceRecognition) {
                            console.log("recog abort")
                            if (this.recog != undefined) this.recog.abort()
                        }
                        if (this.interval != undefined) {
                            console.log('cancel send userstatus')
                            clearInterval(this.interval)
                            this.interval = undefined
                        }
                        this.speechFunc(ut)
                    }
                }
            }
        },
    }
}