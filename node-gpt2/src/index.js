const path = require('path');
const express = require('express');
const morgan = require('morgan');
const app = express();
const ejs = require('ejs');
const session = require('express-session');

// settings
app.set('port', process.env.PORT || 3000);
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'ejs');

//session
app.use(session({
    secret: '34SDgsdgspxxxxxxxdfsG', // just a long random string
    resave: false, //fuerza a que se guarde si es true
    saveUninitialized: true,
}));

// middlewares
app.use(morgan('dev'));
app.use(express.urlencoded({ extended: false }));
app.use(express.json());

// routes
//app.use('/api/products', require('./routes/index'));
app.use(require("./routes/index.routes"));

app.use(require("./routes/books.routes"));

// static files
app.use(express.static(path.join(__dirname, 'public')));

// start the server
app.listen(app.get('port'), () => {
    console.log(`server on port ${app.get('port')}`);
});