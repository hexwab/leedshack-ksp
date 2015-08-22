var C=document.getElementById("c");
var c=C.getContext("2d");
var planet = { r: 2000 };
/* (r,theta) are polar coords wrt planet. phi is rotation */
var ship = { x: 0, y: planet.r, dx: 0, dy: 0, phi: Math.PI/2, dphi: 0,
	     theta:0, dtheta: 0,
	     maxthrust: .02, thrust: 0 };
var crashed = false;
var landed = false;
var zoom=1;
var d=document.getElementById("d");
function frame() {
    c.fillStyle="cyan";
    c.fillRect(0,0,320,256);
    c.save();
    c.translate(-160,-128);
    c.scale(zoom,zoom);
    c.rotate(ship.phi);

// draw ground
    c.fillStyle="#008000";//"#808080";
    c.beginPath();
    c.arc(ship.x,ship.y,planet.r,2*Math.PI,false);
    c.fill();
    c.restore();

    //draw ship
    c.fillStyle="black";
    c.fillRect(160,128,4,-16);

    //thrust
    ship.dx += ship.maxthrust * ship.thrust * Math.cos(ship.phi);
    ship.dy += ship.maxthrust * ship.thrust * Math.sin(ship.phi);
    var dr = Math.sqrt(ship.dx*ship.dx+ship.dy*ship.dy);
    var r = Math.sqrt(ship.x*ship.x+ship.y*ship.y);
    var theta = Math.atan2(ship.y,ship.x);

    ship.phi+=ship.dphi;
    ship.x += ship.dx;
    ship.y += ship.dy;

    landed = false;
    if (Math.abs(r-planet.r)<=-dr &&
	Math.abs(dr) < 0.5 &&
		1 /* FIXME: rotation */
       ) {
	ship.dx = ship.dy = 0;
	landed=true;
    } else if (r < planet.r) {
	/* crashed */
	crashed = true;
	alert("crashed");
    } else {
	var g = 0.01;
//	ship.dx -= g * Math.cos(theta);
//	ship.dy -= g * Math.sin(theta);

    }
    c.restore();
//    d.innerHTML = "r="+ship.r+"\ndr="+ship.dr+"\ntheta="+ship.theta+"\ndtheta="+ship.dtheta+"\nthrust="+ship.thrust+(landed?"\nlanded":"");
    d.innerHTML = "x="+ship.x+" dx="+ship.dx+"\ny="+ship.y+" dy="+ship.dy+
	"\nr="+r+" dr="+dr+
	"\nphi="+ship.phi+" dphi="+ship.dphi+
	"\ntheta="+theta+"\ndtheta="+ship.dtheta+"\nthrust="+ship.thrust+(landed?"\nlanded":"");
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

    case "+": zoom *= 2; break;
    case "-": zoom -= 2; break;
    }
};

setInterval(function(){    console.log(ship); } , 1000);
