let r, g, b, sw;
let unitDist, radius;
let w = 178*2, h = 218*2;
let up_m, dn_m, lf_m, rt_m;
let pos_axis;
let rec_w, rec_h22offset;

let numbers;
let nums = [0, 0, 0, 0, 0];

function setup() {
  var theCanvas = createCanvas(w, h);
  theCanvas.parent("#cv");

  setupFaceTracking();
  
  numbers = true;
}


function draw() {
  background(0);

  updateFaceTracking();
  displayFaceTracking();
  
  // Face tracking pattern

  if (fPositions.length > 0) {
    // if there is more than one face!
    
    r = 255;
    g = 255;
    b = 255;
    sw = 2;
    
    //Face
    
    linkConsecDots(0, 18, r, g, b, sw);
    linkConsecDots(19, 22, r, g, b, sw);
    linkTwoDots(0, 19, r, g, b, sw);
    linkTwoDots(18, 22, r, g, b, sw);
    
    //Right Eye
    
    linkConsecDots(23, 26, r, g, b, sw);
    linkTwoDots(23, 26, r, g, b, sw);
    
    //Left Eye
    
    linkConsecDots(28, 31, r, g, b, sw);
    linkTwoDots(28, 31, r, g, b, sw);
    
    //Nose
    
    linkConsecDots(33, 40, r, g, b, sw);
    linkTwoDots(33, 40, r, g, b, sw);
    linkTwoDots(33, 41, r, g, b, sw);
    linkTwoDots(41, 62, r, g, b, sw);
    linkTwoDots(42, 62, r, g, b, sw);
    linkTwoDots(43, 62, r, g, b, sw);
    linkTwoDots(42, 35, r, g, b, sw);
    linkTwoDots(42, 36, r, g, b, sw);
    linkTwoDots(43, 38, r, g, b, sw);
    linkTwoDots(43, 39, r, g, b, sw);

    //Mouth
    
    linkConsecDots(44, 55, r, g, b, sw);
    linkConsecDots(56, 58, r, g, b, sw);
    linkConsecDots(59, 61, r, g, b, sw);
    linkTwoDots(44, 55, r, g, b, sw);
    linkTwoDots(44, 56, r, g, b, sw);
    linkTwoDots(44, 61, r, g, b, sw);
    linkTwoDots(50, 58, r, g, b, sw);
    linkTwoDots(50, 59, r, g, b, sw);
    
    //Face
    
    linkTwoDots(19, 23, r, g, b, sw);
    linkTwoDots(15, 28, r, g, b, sw);
    linkTwoDots(20, 24, r, g, b, sw);
    linkTwoDots(16, 29, r, g, b, sw);
    linkTwoDots(21, 24, r, g, b, sw);
    linkTwoDots(17, 29, r, g, b, sw);
    linkTwoDots(22, 25, r, g, b, sw);
    linkTwoDots(18, 30, r, g, b, sw);
    linkTwoDots(22, 33, r, g, b, sw);
    linkTwoDots(18, 33, r, g, b, sw);
    linkTwoDots(25, 33, r, g, b, sw);
    linkTwoDots(30, 33, r, g, b, sw);
    linkTwoDots(25, 35, r, g, b, sw);
    linkTwoDots(30, 39, r, g, b, sw);
    // linkTwoDots(35, 44, r, g, b, sw);
    // linkTwoDots(39, 50, r, g, b, sw);
    linkTwoDots(37, 47, r, g, b, sw);
    // linkTwoDots(37, 46, r, g, b, sw);
    // linkTwoDots(37, 48, r, g, b, sw);
    linkTwoDots(36, 46, r, g, b, sw);
    linkTwoDots(38, 48, r, g, b, sw);
    // linkTwoDots(36, 45, r, g, b, sw);
    // linkTwoDots(38, 49, r, g, b, sw);
    linkTwoDots(0, 23, r, g, b, sw);
    linkTwoDots(14, 28, r, g, b, sw);
    linkTwoDots(26, 35, r, g, b, sw);
    linkTwoDots(31, 39, r, g, b, sw);
    linkTwoDots(1, 35, r, g, b, sw);
    linkTwoDots(13, 39, r, g, b, sw);
    linkTwoDots(2, 35, r, g, b, sw);
    linkTwoDots(12, 39, r, g, b, sw);
    linkTwoDots(2, 45, r, g, b, sw);
    linkTwoDots(12, 49, r, g, b, sw);
    linkTwoDots(3, 44, r, g, b, sw);
    linkTwoDots(11, 50, r, g, b, sw);
    linkTwoDots(4, 44, r, g, b, sw);
    linkTwoDots(10, 50, r, g, b, sw);
    linkTwoDots(5, 55, r, g, b, sw);
    linkTwoDots(9, 51, r, g, b, sw);
    linkTwoDots(1, 26, r, g, b, sw);
    linkTwoDots(13, 28, r, g, b, sw);
    linkTwoDots(6, 54, r, g, b, sw);
    linkTwoDots(8, 52, r, g, b, sw);
    linkTwoDots(7, 53, r, g, b, sw);
    
    fill(r, g, b);
    noStroke();
    
    unitDist = distByIndex(0, 1);
    radius = map(unitDist, 20, 200, 5, 20);
    // text(unitDist, 10, 10);
    
    
    // Rectangular frame
    
    up_m = h;
    dn_m = 0;
    lf_m = w;
    rt_m = 0;
    
    for (let i = 0; i < fPositions.length; i ++) {
      
      pos_axis = fPositions[i];
      
      if (pos_axis.x > rt_m) {
        rt_m = pos_axis.x;
      }
      
      if (pos_axis.x < lf_m) {
        lf_m = pos_axis.x;
      }
      
      if (pos_axis.y > dn_m) {
        dn_m = pos_axis.y;
      }
      
      if (pos_axis.y < up_m) {
        up_m = pos_axis.y;
      }
      
      // ellipse(fPositions[i].x, fPositions[i].y, radius, radius);

    }
    
    offset = 10;
    
    rt_m += offset;
    lf_m -= offset;
    dn_m += offset;
    up_m -= offset;
    
    rec_w = rt_m - lf_m;
    rec_h = dn_m - up_m;
    
    noFill();
    stroke(255);
    rect(lf_m, up_m, rec_w, rec_h);
    
    
    // Numbers
    
    if (numbers) {
      
      nums[0] = distByIndex(23, 25);
      nums[1] = distByIndex(28, 30);
      nums[2] = distByIndex(35, 39);
      nums[3] = distByIndex(44, 50);
      nums[4] = distByIndex(2, 12);
      
      fill(255, 150);
      noStroke();
      textAlign(CENTER);
      
      // console.log(fPositions);
      
      text(nums[0], fPositions[26].x, fPositions[26].y);
      text(nums[1], fPositions[29].x, fPositions[29].y);
      text(nums[2], fPositions[44].x, fPositions[44].y);
      text(nums[3], fPositions[39].x, fPositions[39].y);
      text(nums[4], fPositions[9].x, fPositions[9].y);
      
    }
    
  }

}




function linkTwoDots(dot1, dot2, r, g, b, sw) {  
  stroke(r, g, b);
  strokeWeight(sw);
  line(fPositions[dot1].x, fPositions[dot1].y, fPositions[dot2].x, fPositions[dot2].y);
}

function linkConsecDots(start, end, r, g, b, sw) {
  
  stroke(r, g, b);
  strokeWeight(sw);
  for (let i = start; i < end; i++) {
    line(fPositions[i].x, fPositions[i].y, fPositions[i+1].x, fPositions[i+1].y);
  }
}

function distByIndex(a, b) {
  
  return dist(fPositions[a].x, fPositions[a].y, fPositions[b].x, fPositions[b].y);
  
}

function posByIndex(a, xORy) {
  
  return fPositions[a][xORy];
  
}






// This example code is based on Kyle McDonald's CV examples
// and adjusted for beginner level students.

// https://kylemcdonald.github.io/cv-examples/
// https://github.com/kylemcdonald/AppropriatingNewTechnologies/wiki/Week-2

var capture;
var tracker;
let fPositions = [];

function setupFaceTracking() {
  capture = createCapture({
    audio: false,
    video: {
      width: w,
      height: h
    }
  }, function() {
    console.log('capture ready.')
  });
  capture.elt.setAttribute('playsinline', '');
  //createCanvas(w, h);
  capture.size(w, h);
  capture.hide();

  tracker = new clm.tracker();
  tracker.init();
  tracker.start(capture.elt);
}

function updateFaceTracking() {
  var positions = tracker.getCurrentPosition();
  if (positions.length > 0) {
    fPositions = [];
  }
  for (var i = 0; i < positions.length; i++) {
    fPositions.push(new FacePosition(positions[i][0], positions[i][1], i));
  }
}

function displayFaceTracking() {
  push();
  
  colorMode(HSB);
  
  image(capture, 0, 0, w, h);
  var positions = tracker.getCurrentPosition();

  // noFill();
  // stroke(255);
  // beginShape();
  // for (var i = 0; i < positions.length; i++) {
  //   vertex(positions[i][0], positions[i][1]);
  // }
  // endShape();

  noStroke();
  for (var i = 0; i < positions.length; i++) {
    fill(map(i, 0, positions.length, 0, 360), 50, 100);
    // ellipse(positions[i][0], positions[i][1], 4, 4);
    // text(i, positions[i][0], positions[i][1]);
  }

  if (positions.length > 0) {
    var mouthLeft = createVector(positions[44][0], positions[44][1]);
    var mouthRight = createVector(positions[50][0], positions[50][1]);
    var smile = mouthLeft.dist(mouthRight);
    // uncomment the line below to show an estimate of amount "smiling"
    // rect(20, 20, smile * 3, 20);

    // uncomment for a surprise
    // noStroke();
    // fill(0, 255, 255);
    // ellipse(positions[62][0], positions[62][1], 50, 50);
  }
  
  pop();
}


class FacePosition {
  constructor(x, y, i) {
    this.x = x;
    this.y = y;
    this.index = i;
  }
}