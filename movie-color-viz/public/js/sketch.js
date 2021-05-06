let img1;
let img2;
let img3;
let img4;
let img5;

function preload() {
  img1 = loadImage('https://image.tmdb.org/t/p/original//gcjudvipceuhvmozuvhoj1jyqfv.jpg');
}

function setup() {
  createCanvas(200, 150)
  image(theImage, 0, 0)
  theImage.loadPixels()
  
  for(let j=0 ; j < theImage.pixels.length ;j+=4) {

    let r = theImage.pixels[j];
    let g = theImage.pixels[j+1]
    let b = theImage.pixels [j+2]


    let temp = colors.find((element) => {
        return element.color[0] == r &&
        element.color[1] == g &&
        element.color[2] == b;
    });


    if (!temp) {
        colors.push({ color: [r, g, b], amount: 1});  
    } else {
        temp.amount += 1; 
    }
    colors = colors.sort((a, b) => b.amount - a.amount)
  }
  
  fill(colors[0].color)
  rect(150, 0, 50, 30)
  fill(colors[1].color)
  rect(150, 30, 50, 30)
  fill(colors[2].color)
  rect(150, 60, 50, 30)
  fill(colors[3].color)
  rect(150, 90, 50, 30)
  fill(colors[4].color)
  rect(150, 120, 50, 30)
}

function draw() {

}