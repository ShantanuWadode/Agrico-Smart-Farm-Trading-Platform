const express = require('express');
const app = express();
const bodyParser = require('body-parser');
app.use(bodyParser.urlencoded({extended: false}));
app.use(bodyParser.json());
app.use(express.static('public'));
const pug = require('pug');
const path  = require('path');
app.set("view engine", "pug");
app.set('views', path.join(__dirname, '../views'));
const router = require('./routes/index.js');
app.use(router);


const PORT = process.env.PORT || 3003;

app.listen(PORT, '0.0.0.0', () => {
    console.log(`Server running on http://0.0.0.0:${PORT}`);
  });