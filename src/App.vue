<template>
  <v-app>
    <v-content>
      <v-container fluid>
        <v-slide-y-transition mode="out-in">
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
        </v-slide-y-transition>
      </v-container>
	  
	  <v-flex xs12 sm6 offset-sm3>
      <v-card>
        <v-form v-model="valid" ref="form" lazy-validation>
    <v-text-field
      label="ссылка в формате m.avito..."
      v-model="urlParse"
      :rules="urlParseRules"
      required
    ></v-text-field>
    <v-text-field
      label="количество ads"
      v-model="countAds"
      :rules="countAdsRules"
      required
    ></v-text-field>
    
    <v-btn
      @click="submit"
      :disabled="!valid"
    >
      запустить парсер
    </v-btn>
    <v-btn @click="clear">очистить поля</v-btn>
  </v-form>
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
		 valid: true,
        clipped: false,
        drawer: true,
        fixed: false,
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
        items: [{
          icon: 'bubble_chart',
          title: 'Inspire'
        }],
        miniVariant: false,
        right: true,
        rightDrawer: false,
        title: 'Vuetify.js'
      }
    },
	methods: {
      submit () {
        if (this.$refs.form.validate()) {
			console.log(this.urlParse);
			console.log(this.countAds);
			location.href = 'http://185.143.173.66:5000/start?url=' + this.urlParse + '&count=' + this.countAds;
        }
      },
      clear () {
        this.$refs.form.reset()
      }
    }
  }
</script>
