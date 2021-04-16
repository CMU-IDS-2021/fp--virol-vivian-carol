let screenWidth;
let screenHeight;
let videoUrl = document.getElementById("trailer-url").innerHTML + '/';

let capture;

let lastTimeCheck = 0;
let stampSpeed = 1000; // how fast the sketch
                       // samples the video's color
let drawIndex = 0;
let lineWeight = 6;

let blackBar = 0; //fill this number if the video has black bars

function setup() {
  screenWidth = innerWidth;
  screenHeight = innerHeight;

  let canvas = createCanvas(screenWidth * 0.6, screenHeight * 0.6);
  canvas.parent("canvas");

  video = createVideo(videoUrl, vidLoad);
  video.size(width/2, height/2);
  // video.play();
}

function vidLoad() {
  let redTotal = 0;
  let blueTotal = 0;
  let greenTotal = 0;

  noStroke();

  video.loadPixels();

  for (let cx = 0; cx < video.width; cx ++) {
    for (let cy = 0; cy < video.height; cy ++) {

      if (cy > blackBar && cy < video.height - blackBar) {
        let offset = int(((cy * video.width) + cx) * 4);
        let redc = video.pixels[offset];
        let greenc = video.pixels[offset + 1];
        let bluec = video.pixels[offset + 2];

        redTotal += redc;
        //console.log(redTotal);
        greenTotal += greenc;
        blueTotal += bluec;

        fill(redc, greenc, bluec);

      }
    }
  }

  let redAvg = int(redTotal / (video.width * video.height));
  //console.log(redAvg);
  let greenAvg = int(greenTotal / (video.width * video.height));
  let blueAvg = int(blueTotal / (video.width * video.height));

  if (millis() - lastTimeCheck > stampSpeed) {
    console.log(redAvg + "," + greenAvg + "," + blueAvg);
    fill(redAvg, greenAvg, blueAvg);
    noStroke();
    rect(drawIndex * lineWeight, 0, lineWeight, height);
    drawIndex++;
    lastTimeCheck = millis();
  }
}

function draw() {  
}
