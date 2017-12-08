# solid-octo-dollop
pyton avito parser
### Running back-end
Just run make in the project directory: 
```
make
```
## Frontend Build Setup

``` bash
# install dependencies
npm install

# serve with hot reload at localhost:8080
npm run dev

# build for production with minification
npm run build

# build for production and view the bundle analyzer report
npm run build --report
```


### Usage backend
Login - admin; password - admin

`/` - get status of parser

`/result` - get parsed phone numbers

`/start?url=[Avito url to parse (e.g. https://m.avito.ru/engels/komnaty)]&count=[count of ads to parse]` - start parser

`/stop` - stop parser

`/clear` - clear all phone numbers
