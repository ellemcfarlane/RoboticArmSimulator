let canvas=document.getElementById("canvas");
const ctx = canvas.getContext("2d");
const width = canvas.width;
const height = canvas.height;
ctx.lineWidth = 2;
const tableHeight = 5*height/6;
const scale = 1.0;
const home_y = tableHeight - 2;
const home_x = width / 2;
const hand_home_x = 143;
const hand_home_y = 85;
const canvasOffset=$("#canvas").offset();
const offsetX=canvasOffset.left;
const offsetY=canvasOffset.top;
let init_claw_ang = 45;
let init_bic_ang = 45;
let prev_claw_ang;
let claw = document.getElementById("claw");
const claw_offsetX = -15;// claw.width;
const claw_offsetY = -15;// claw.height;

function set_up() {
    moveImage("base", home_x-200, home_y);
    draw_initial_arm();
    set_color('#000000');
    draw_axes();
}

function reset() {
    clear_screen();
    set_up();
}

function draw_table() {
    set_color('#cc5500');
    ctx.fillRect(0,tableHeight+1, canvas.width, height-tableHeight);
}

function draw_axes() {
    ctx.beginPath();
    set_color('#000000');
    ctx.moveTo(0, tableHeight);
    ctx.lineTo(width, tableHeight);
    ctx.stroke();
}

function draw_arm(arm_data) {
    clear_screen();
    ctx.lineWidth = 10;
    // draw first arm segment
    // console.log("actual" + arm_data['elbow_y'])
    // console.log("scale" + scale)
    // console.log("scaled" + scale*arm_data['elbow_y'])
    let to_x1 = home_x + scale*arm_data['elbow_x'];
    let to_y1 = home_y - scale*arm_data['elbow_y'];
    let YELLOW = "#FFCC00";
    draw_line([home_x, home_y], [to_x1, to_y1], YELLOW)
    // draw second arm segment
    let to_x2 = home_x + scale*arm_data['hand_x'];
    let to_y2 = home_y - scale*arm_data['hand_y'];
    let RED = "#FF0000";
    draw_line([to_x1, to_y1], [to_x2, to_y2], RED)
}

function update_claw_angle(arm_data) {
    moveImage("claw", hand_home_x+home_x,
        hand_home_y+290);
    let bicep_angle = parseFloat(arm_data['bicep_angle']);
    let forearm_angle = parseFloat(arm_data['forearm_angle']);
    let claw_angle = -forearm_angle-bicep_angle;
    rotateImage("claw", -(init_claw_ang-claw_angle), "top left");
    prev_claw_ang = claw_angle;
}

function draw_initial_arm() {
    set_hand_pos(hand_home_x, hand_home_y);
    fetch('/get_arm_data').then(function(data){
        return data.json();
    }).then(function (arm_data) {
        update_claw_angle(arm_data);
        draw_arm(arm_data);
    }).catch((error) => {
      console.error('Error:', error);
    });
}

function set_color(color_value){
    ctx.strokeStyle = color_value;
    ctx.fillStyle = color_value;
}

function draw_line(from, to, color) {
    ctx.beginPath();
    set_color(color);
    ctx.moveTo(from[0], from[1]);
    ctx.lineTo(to[0], to[1]);
    ctx.stroke();
}

function set_hand_pos(x, y) {
    const message = {'x': x, 'y': y};
    fetch('/get_arm_data', {
        method: 'POST',
        body: JSON.stringify(message)
    }).then(function (data) {
        return data.json();
    }).then(function (arm_data) {
        if (!arm_data['successful']) {
            console.log("Can't reach fam");
        }
        else { //success
            draw_arm(arm_data);
        }
    }).catch((error) => {
        console.error('Error:', error);
    });
}

$("body").mousemove(function(e){handleMouseMove(e);});
function handleMouseMove(e) {
    let mouseX=parseInt(e.clientX-offsetX);
    let mouseY=parseInt(e.clientY-offsetY);
    // restrict claw height to table
    if (mouseY >= home_y - 60) return;
    const message = {'x': mouseX - home_x, 'y': home_y - mouseY};
    fetch('/get_arm_data', {
        method: 'POST',
        body: JSON.stringify(message)
    }).then(function (data) {
        return data.json();
    }).then(function (arm_data) {
        if (!arm_data['successful']) {
            // console.log("Can't reach.");
        }
        else { //success
            update_claw_angle(arm_data);
            // code to try to fix the claw offset issue
            // let adjust = tanFromDegrees(prev_claw_ang);
            // console.log("adj", adjust);
            // console.log("claw ang", prev_claw_ang);
            // let bicep_angle = parseFloat(arm_data['bicep_angle']);
            // let forearm_angle = parseFloat(arm_data['forearm_angle']);
            // console.log("sho ang", forearm_angle);
            // console.log("bic ang", bicep_angle);
            //moveImage("claw", mouseX-claw_offsetX - 100, mouseY-claw_offsetY-adjust*100);
            moveImage("claw", mouseX-claw_offsetX, mouseY-claw_offsetY);
            draw_arm(arm_data);
        }
    }).catch((error) => {
        console.error('Error:', error);
    });
}

function clear_screen() {
    ctx.lineWidth = 3;
    ctx.clearRect(0,0, canvas.width, canvas.height);
    draw_table();
    draw_axes();
}

function moveImage(IDname, newX, newY) {
    let image = $("#" + IDname);
    image.css("left", newX + "px");
    image.css("top", newY + "px");
}

function imgError(image) {
    image.onerror = "";
    image.src = "/images/noimage.gif";
    console.log("image error");
    return true;
}

function rotateImage(IDname, degrees, mode="center") {
    let image = $("#" + IDname);
    image.css("transform-origin", mode);
    image.css("transform", 'rotate(' + degrees + 'deg)');
}

function tanFromDegrees(degrees) {
  return Math.tan(degrees * Math.PI/180);
}