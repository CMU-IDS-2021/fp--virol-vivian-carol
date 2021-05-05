$(document).ready(() => {
  console.log('connected');

  // show original movie color template if checkbox is checked
  let isChecked = $('#show-original-checkbox').is(':checked');

  $('#show-original-checkbox').click(() => {
    isChecked = !isChecked;

    if (isChecked) {
      $('#original-average-color').css({'display': 'block'});
    } else {
      $('#original-average-color').css({'display': 'none'});
    }
  });

  $('#submit-button').click(() => {
    console.log('making POST request');

    // display loading message
    $('.message-div').css({'display': 'block'});

    $('#message-text').text('loading ...');
    $('#message-text').css({
      'background-color': 'black',
      'color': 'white'
    });

    // make post request
    $.ajax({
      type: "POST",
      data : $('#form').serialize(),
      dataType: 'json',
      success: (data) => {
          // console.log(data);
          // $(".recommended-title").text(data['recommended'][0]['title']);
      }
    });
  });

  // get django template data
  const dataVal = $('#data').val();

  if (dataVal && dataVal != "") {
    const data = JSON.parse($('#data').val());
    console.log(data);


    // recommended
    if (data['recommended'].length > 0) { 
      // recommendations found
      
      // show checkbox
      if (data['image'] != "" && data['image'] != '/app/images/') {
        $('#original-movie-average-color').css({'display': 'block'});
        $('#checkbox-label').text('show average movie trailer colors for ' + data['movie']);
      }

      $('.results').css({'display': 'block'});
      $('.message-div').css({'display': 'none'});
      
      // add average color for original movie
      $('#original-average-color').attr('src', 'static/app/images/originalmovie.png');

      // add title, image, overview for recommended movies
      currDataIndex = 0;
      recommended = data['recommended'];
      currRec = recommended[currDataIndex];

      $("#recommended-title").text(currRec['title']);
      $("#card-average-color").attr('src', 'static' + currRec['image']);
      $("#recommended-overview").text(currRec['data']['overview']);

      $('#next-rec-button').click(() => {
        if (currDataIndex == Object.keys(recommended).length - 1) {
          currDataIndex = 0;
        } else {
          currDataIndex += 1;
        }
        currRec = recommended[currDataIndex];

        $("#recommended-title").text(currRec['title']);
        $("#card-average-color").attr('src', 'static' + currRec['image']);
        $("#recommended-overview").text(currRec['data']['overview']);
      });

    } else {
      // no recommendataions found
      $('.results').css({'display': 'none'});
      $('.message-div').css({'display': 'block'});

      // add error message
      $('#message-text').text('no recommendations found for this movie. please try searching for another movie.');
      $('#message-text').css({
        'background-color': 'red',
        'color': 'white'
      });
    }
  }
  

});