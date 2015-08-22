var C=document.getElementById("c");
var c=C.getContext("2d");
var planet = { r: 2000 };
/* (r,theta) are polar coords wrt planet. phi is rotation */
var ship = { r: planet.r, theta: 0, dr: 0, dtheta: 0, phi: Math.PI/2, dphi: 0,
	     maxthrust: .02, thrust: 0 };
var crashed = false;
var landed = false;
function hatch(c,c1,c2) {
    var t=document.createElement("canvas");
    var s=1;
    t.width=t.height=s*2;
    var T=t.getContext("2d");
//    T.translate(0.5,0.5);
    T.fillStyle=c1;
    T.fillRect(0,0,s*2,s*2);
    T.fillStyle=c2;
    T.fillRect(0,0,s,s);
    T.fillRect(s,s,s,s);
    return c.createPattern(t,'repeat');
}

var d=document.getElementById("d");
function frame() {
    c.save();
//    c.imageSmoothingEnabled=
//	c.mozImageSmoothingEnabled=
//	c.webkitImageSmoothingEnabled=false;
//    c.translate(0.5,0.5);
    c.fillStyle=hatch(c,"#0ff","#f0f");//"cyan";
    c.fillRect(0,0,320,256);
    c.translate(160,128);
    c.rotate(ship.phi);
// draw ground
    c.fillStyle=hatch(c,"#0f0","#000");//"#008000";//"#808080";
    var x = ship.r*Math.cos(ship.theta);
    var y = ship.r*Math.sin(ship.theta);
    c.beginPath();
    c.arc(x,y,planet.r,2*Math.PI,false);
    c.fill();
    c.restore();
//draw ship
    c.fillstyle="black";
    c.fillRect(158,128,4,16);
    ship.dr += ship.maxthrust * ship.thrust;
    ship.r += ship.dr;
    ship.theta+=ship.dtheta;
    ship.phi+=ship.dphi;
    landed = false;
    if (Math.abs(ship.r-planet.r)<=-ship.dr &&
	Math.abs(ship.dr) < 0.5 &&
		1 /* FIXME: rotation */
       ) {
	/* on the surface */
	ship.r = planet.r;
	ship.dr = 0;
	landed=true;
    } else if (ship.r < planet.r) {
	/* crashed */
	crashed = true;
	alert("crashed");
    } else {
	ship.dr -= 0.01; // gravity
    }
    d.innerHTML = "r="+ship.r+"\ndr="+ship.dr+"\ntheta="+ship.theta+"\ndtheta="+ship.dtheta+"\nthrust="+ship.thrust+(landed?"\nlanded":"");
    if (!crashed)
	requestAnimationFrame(frame);
}

requestAnimationFrame(frame);
//frame();
window.onkeypress=function(e) {
    console.log(e);
    switch (e.key) {
    case "x": ship.thrust = 0; break;
    case "z": ship.thrust = 1; break; /* 100% */
    case "w": //dx += .1*Math.cos(ship.phi); dy += .1*Math.sin(ship.phi); 
	//ship.dr += .1; break;
	ship.thrust += 1/16;
	if (ship.thrust > 1)
	    ship.thrust = 1;
	break;
    case "s": //dx -= .1*Math.cos(ship.phi); ship.dy -= .1*Math.sin(ship.phi); break;
	//ship.dr -= .1; break;
	ship.thrust -= 1/16;
	if (ship.thrust < 0)
	    ship.thrust = 0;
	break;
    case "a": ship.dphi += .001; break;
    case "d": ship.dphi -= .001; break;
    }
};

setInterval(function(){    console.log(ship); } , 1000);
