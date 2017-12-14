<template>
  <v-app>
    <v-content>
      <v-container fluid>
        <v-layout column align-center>
          <img src="/static/v.png" alt="Vuetify.js" class="mb-5" />
          <blockquote>
            solid-octo-dollop
            <footer>
              <small>
                <em>&mdash;written with python & vuejs</em>
              </small>
            </footer>
          </blockquote>
          </v-layout>
      </v-container>

      <v-flex xs12 sm6 offset-sm3>
        <v-card>
          <v-form v-model="valid" ref="form" lazy-validation>
            <v-text-field
              label="ссылка в формате m.avito..."
              v-model="urlParse"
              :rules="urlParseRules"
              required>
            </v-text-field>
            <v-text-field
              label="количество ads"
              v-model="countAds"
              :rules="countAdsRules"
              required
            ></v-text-field>

            <v-btn
              @click="submit"
              :disabled="!valid">
              запустить парсер
            </v-btn>
            <v-btn @click="clear">очистить поля</v-btn>
          </v-form>
          <v-progress-circular
            v-bind:size="100"
            v-bind:width="15"
            v-bind:rotate="-90"
            v-bind:value="progressValue"
            color="primary"
          >
            {{progressCurrent}}/{{progressEnd}}
          </v-progress-circular>
        </v-card>
      </v-flex>
    </v-content>

    <v-footer :fixed="fixed" app>
      <span>&copy; 2017</span>
    </v-footer>

  </v-app>
</template>

<script>
  export default {
    data () {
      return {
        interval: {},
        progressCurrent: '0',
        progressEnd: '0',
        progressValue: '0',
        urlParse: '',
        urlParseRules: [
            (v) => !!v || 'Требуется ссылка',
            (v) => /m\.avito/.test(v) || 'ссылка на моб версию!'
        ],
        countAds: '',
        countAdsRules: [
            (v) => !!v || 'Требуется количество',
            (v) => /[0-9]/.test(v) || 'цифрами писать надо'
        ],
        title: 'Vuetify.js'
      }
    },
    beforeDestroy () {
      clearInterval(this.interval)
    },
    mounted () {
      this.interval = setInterval(() => {
        this.$http.get('/api/status').then(response => {
          // get body data
          let progressData = JSON.parse(response.bodyText);
          this.progressCurrent = progressData.current;
          this.progressEnd = progressData.end;
          let onePercent = this.progressEnd / 100;
          this.progressValue = this.progressCurrent / onePercent;
        }, response => {
          console.log(' getProgress err response')
          let progressData = JSON.parse(response.bodyText);
          console.log('Status of getProgress: ' + progressData.status)
          // error callback
        });
      }, 2000)
    },
	  methods: {
      submit () {
        if (this.$refs.form.validate()) {
			console.log(this.urlParse);
			console.log(this.countAds);
      this.$http.get('/api/status').then(response => {
        // get body data
        let progressData = JSON.parse(response.bodyText);
        console.log('progressData:' + progressData);
        this.progressCurrent = progressData.current;
        this.progressEnd = progressData.end;
        let onePercent = this.progressEnd / 100;
        this.progresValue = this.progressCurrent / onePercent;

      }, response => {
        console.log(' getProgress err response')
        // error callback
      });
			location.href = '/api/start?url=' + this.urlParse + '&count=' + this.countAds;
        }
      },
      clear () {
        this.$refs.form.reset()
      }
    }
  }
</script>
