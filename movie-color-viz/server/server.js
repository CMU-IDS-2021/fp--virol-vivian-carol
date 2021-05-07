const express = require('express');
const hbs = require('hbs');
const path = require('path');
const bodyParser = require('body-parser');
const exphbs = require('express-handlebars');
require('dotenv').config();

// set up port
const port = process.env.PORT || 3000;

const app = express();
const server = app.listen(port, () => {
    console.log(`Web server up on port ${port}`);
});

// view engine
app.use(express.static(path.join(__dirname, "../public")));

app.engine('hbs', exphbs({
  extname: '.hbs',
  defaultLayout:false}));
app.set('view engine', 'hbs');

app.engine('html', require('ejs').renderFile);

// middleware
const middleware = require('../middleware/middleware.js')
app.use(express.static(__dirname + '../public'));

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({extended: true}));

app.get('/', (req, res) => {
  res.render('home', {text: ''});
})

app.post('/', async function (req, res){
  console.log(req.body);
  let data;
  let text;
  let num = 5;

  try {
    switch(req.body.viztype) {
      case 'movie':
        data = await middleware.getRecommendedMovies(req.body.textinput, num);
        text = "recommended movies:";
        // console.log('similar movies:', data);
        break;
      case 'producer':
        data = await middleware.getPersonMovies(req.body.textinput, 'producer', num);
        text = "movies:";
        // console.log('producer data:', data);
        break;
      case 'actor':
        data = await middleware.getPersonMovies(req.body.textinput, 'actor', num);
        text = "movies:";
        // console.log('actor data:', data);
        break;
    }

    let movieOne = data[0];
    let movieTwo = data[1];
    let movieThree = data[2];
    let movieFour = data[3];
    let movieFive = data[4];

    if (req.body.viztype == 'movie') {
      let originalMovie = data[5];
      res.render('home', {
        originalMovie: originalMovie,
        text: text,
        type: req.body.viztype,
        input: req.body.textinput,
        movie1: movieOne,
        movie2: movieTwo,
        movie3: movieThree,
        movie4: movieFour,
        movie5: movieFive,
      });
    } else {
      let movie6 = data[6];
      let movie7 = data[7];
      let movie8 = data[8];
      let movie9 = data[9];
      let movie10 = data[10];
      let movie11 = data[11];
      let movie12 = data[12];
      let movie13 = data[13];
      let movie14 = data[14];
      let movie15 = data[15];
    
      res.render('home', {
        text: text,
        type: req.body.viztype,
        input: data.slice(-1),
        movie1: movieOne,
        movie2: movieTwo,
        movie3: movieThree,
        movie4: movieFour,
        movie5: movieFive,
        movie6: movie6,
        movie7: movie7,
        movie8: movie8,
        movie9: movie9,
        movie10: movie10,
        movie11: movie11,
        movie12: movie12,
        movie13: movie13,
        movie14: movie14,
        movie15: movie15,
      });
    }

  } catch (e) {
    res.status(404).send();
  }

});
