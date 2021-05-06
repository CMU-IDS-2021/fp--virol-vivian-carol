"use strict";

$(document).ready(() => {
  console.log('connected');

  $('#submit-button').click(() => {
    // display loading message
    $('.message-div').css({'display': 'block'});

    $('#message-text').text('loading ...');
    $('#message-text').css({
      'background-color': 'white',
      'color': 'black'
    });

    // hide results div
    $('#results-div').css({'display': 'none'});
  });

  // color palettes
  console.log('type:', $('#type').text());
  if ($('#type').text() != "") {
    const swatches = 10;
    const colorThief = new ColorThief();

    // display loading message
    $('.message-div').css({'display': 'block'});

    $('#message-text').text('loading ...');
    $('#message-text').css({
      'background-color': 'white',
      'color': 'black'
    });

    let plot = $('#color-plot');

    for (let i = 0; i <= 15; i++) {
      if (i > 5 && $('#type').text() == 'movie') {
        break;
      }

      let palette = $(`#palette-${i}`);
      let image = $(`#movie-${i}-poster`)[0];

      try {
        setTimeout(() => {
          let dominantColor = colorThief.getColor(image);
          let paletteColors = colorThief.getPalette(image, swatches);
          console.log(paletteColors);
          console.log(dominantColor);

          // add colors to palette
          while (palette.firstChild) palette.removeChild(palette.firstChild);
          paletteColors.reduce( (palette,rgb) => {
            let color = `rgb(${rgb[0]}, ${rgb[1]}, ${rgb[2]})`;        
            let swatch = document.createElement('div');
            swatch.style.setProperty('--color', color);
            swatch.setAttribute('color', color);
            palette.append(swatch);
            return palette;
          }, palette);

          // add swatch to color timeline plot
          if (i > 5) {
            // add dominant color to color plot
            let dColor = `rgb(${dominantColor[0]}, ${dominantColor[1]}, ${dominantColor[2]})`;
            let dContainer = document.createElement('div');
            let dSwatch = document.createElement('div');
            let dYear = document.createElement('p');

            dSwatch.style.setProperty('--color', dColor);
            dSwatch.setAttribute('color', dColor);
            dSwatch.classList.add('plot-swatch');

            dContainer.classList.add('plot-swatch-container');

            let year = $(`#movie-${i}-date`).text().substring(0,4);
            dYear.innerText = year;

            dContainer.append(dSwatch);
            dContainer.append(dYear);
            plot.append(dContainer);
          }

          // hide poster
          $(`#movie-${i}-poster`).css({'display': 'none'});
        }, 2000);

        setTimeout(() => {
          // show results div
          $('#results-div').css({'display': 'block'});
          $('.message-div').css({'display': 'none'});

        }, 2500);
    
      } catch (err) {
        console.log(err);
        let errorText = document.createElement('p');
        errorText.text('could not load palette.');
        errorText.css({'color': 'red'});
        palette.append(swatch);
      }
    }

    // viz type is producer or actor
    if ($('#type').text() != "movie") {
      $('#card-0').css({'display': 'none'}); // hide original movie palette card
      $('.color-plot-div').removeClass('hidden');
    } else {
      $('.color-plot-div').css({'display': 'none'}); // hide color time plot
    }
  }

});