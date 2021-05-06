'use strict';

const axios = require('axios');

const MOVIEDB_API_URL = 'https://api.themoviedb.org/3';
const MOVIEDB_API_KEY = '8bab42520fb79424d47245ab1e5406cf';
const OMDB_API_KEY = 'e6dd17dc';

const distributedCopy = (items, n) => {
  var elements = [items[0]];
  var totalItems = items.length - 2;
  var interval = Math.floor(totalItems/(n - 2));
  for (var i = 1; i < n - 1; i++) {
      elements.push(items[i * interval]);
  }
  elements.push(items[items.length - 1]);
  return elements;
}

const getRequestMovieDB = async (queryUrl) => {
  let result = null;

  await axios.get(`${MOVIEDB_API_URL}${queryUrl}`).then((response) => {
    if (response.status == 200) {
      result = response.data;
    }
  }).catch( (err) => {
    console.log(err);
  });

  return result;
}

const getMovieApiData = async (movieName) => {
  let result = {};

  let data = await getRequestMovieDB(`/search/movie?api_key=${MOVIEDB_API_KEY}&query=${movieName}`);
  let movieData = data['results'][0];

  result['id'] = movieData['id'];
  result['poster url'] = `https://image.tmdb.org/t/p/original/${movieData['poster_path']}`;
  result['backdrop url'] = `https://image.tmdb.org/t/p/original/${movieData['backdrop_path']}`;
  result['overview'] = movieData['overview'];
  result['release date'] = movieData['release_date'];
  
  return result;
}

const getRecommendedMovies = async (movieName, numRecs=5) => {
  let result = [];
  result['type'] = 'movie';

  let movieData = await getMovieApiData(movieName);
  
  let recQueryUrl = `/movie/${movieData["id"]}/similar?api_key=${MOVIEDB_API_KEY}`;
  let recData = await getRequestMovieDB(recQueryUrl);

  for (let i = 0; i < numRecs; i++) {
    let currRecData = recData['results'][i];
    let data = {};

    data['title'] = currRecData['original_title'];
    data['id'] = currRecData['id'];
    data['poster'] = `https://image.tmdb.org/t/p/original/${currRecData['poster_path']}`;
    data['backdrop'] = `https://image.tmdb.org/t/p/original/${currRecData['backdrop_path']}`;
    data['overview'] = currRecData['overview'];
    data['date'] = currRecData['release_date'];

    result.push(data);
  }

  // add current movie
  let queryUrl = `/movie/${movieData["id"]}?api_key=${MOVIEDB_API_KEY}`;
  let queryData = await getRequestMovieDB(queryUrl);
  let originalData = {};

  originalData['title'] = queryData['original_title'];
  originalData['id'] = queryData['id'];
  originalData['poster'] = `https://image.tmdb.org/t/p/original/${queryData['poster_path']}`;
  originalData['backdrop'] = `https://image.tmdb.org/t/p/original/${queryData['backdrop_path']}`;
  originalData['overview'] = queryData['overview'];
  originalData['date'] = queryData['release_date'];

  result.push(originalData);

  return result;
}

const filterDictList = (dictList) => {
  // filter out tv shows
  dictList = dictList.filter(function(e) {
    return e.media_type && e.media_type == 'movie';
  });

  // filter duplicate movie titles
  const filteredList = dictList.reduce((acc, current) => {
    const x = acc.find(item => item.original_title === current.original_title);
    if (!x) {
      return acc.concat([current]);
    } else {
      return acc;
    }
  }, []);

  return filteredList;
}

const getPersonMovies = async (name, personType, numMovies=5) => {
  let result = [];
  result['type'] = personType;

  // first, get person id
  let searchData = await getRequestMovieDB(`/search/person?api_key=${MOVIEDB_API_KEY}&query=${name}`);
  let personId = searchData['results'][0]['id'];

  // get movies
  let worksData = await getRequestMovieDB(`/person/${personId}/combined_credits?api_key=${MOVIEDB_API_KEY}`);
  let sortedListByPopularity;
  let sortedListByReleaseDate;
  let timelineList;
  
  if (personType == 'producer') {
    let crewList = worksData['crew'];
    crewList = filterDictList(crewList);

    // sort list by popularity (descending)
    sortedListByPopularity = crewList.sort(function(first, second) {
      return second.popularity - first.popularity;
    });

    // sort list by release date (ascending) and choose 10 evenly spaced movies
    sortedListByReleaseDate = crewList.sort(function(first, second) {
      return Date.parse(first.release_date) - Date.parse(second.release_date);
    });
    timelineList = distributedCopy(sortedListByReleaseDate, 10);

  } else if (personType == 'actor') {
    let castList = worksData['cast'];
    castList = filterDictList(castList);

    sortedListByPopularity = castList.sort(function(first, second) {
      return second.popularity - first.popularity;
    });

    sortedListByReleaseDate = castList.sort(function(first, second) {
      return Date.parse(first.release_date) - Date.parse(second.release_date);
    });
    timelineList = distributedCopy(sortedListByReleaseDate, 10);
  }

  // populate list with most popular movies
  for (let i = 0; i < numMovies; i++) {
    let currMovieData = sortedListByPopularity[i];
    let data = {};

    data['title'] = currMovieData['original_title'];
    data['id'] = currMovieData['id'];
    data['poster'] = `https://image.tmdb.org/t/p/original/${currMovieData['poster_path']}`;
    data['backdrop'] = `https://image.tmdb.org/t/p/original/${currMovieData['backdrop_path']}`;
    data['overview'] = currMovieData['overview'];
    data['date'] = currMovieData['release_date'];
    data['timeline'] = false;

    result.push(data);
  }

  // populate list with 10 evenly spaced movies by release date
  for (let j = 0; j < 10; j++) {
    let currSelection = timelineList[j];
    let currData = {};

    currData['title'] = currSelection['original_title'];
    currData['id'] = currSelection['id'];
    currData['poster'] = `https://image.tmdb.org/t/p/original/${currSelection['poster_path']}`;
    currData['backdrop'] = `https://image.tmdb.org/t/p/original/${currSelection['backdrop_path']}`;
    currData['overview'] = currSelection['overview'];
    currData['date'] = currSelection['release_date'];
    currData['timeline'] = true;

    console.log(currData);
    result.push(currData);
  }

  return result;
}



module.exports = {
  getRecommendedMovies,
  getPersonMovies
};
