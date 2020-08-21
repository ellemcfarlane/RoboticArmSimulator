let canvas=document.getElementById("canvas");
const ctx = canvas.getContext("2d");
const width = canvas.width;
const height = canvas.height;
ctx.lineWidth = 2;
const tableHeight = 5*height/6;
const scale = 1.0;
const base_home_y = tableHeight-10;
const base_home_x = width / 2 + 50;
const hand_home_x = width/4;
const hand_home_y = height/6 - 21;
const canvasOffset=$("#canvas").offset();
const offsetX=canvasOffset.left;
const offsetY=canvasOffset.top;

function draw_screen() {
    move_image("base", base_home_x-200, base_home_y);
    draw_initial_arm();
    set_color('#000000');
    draw_axes();
}

function reset() {
    clear_screen();
    draw_screen();
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
    let to_x1 = base_home_x + scale*arm_data['elbow_x'];
    let to_y1 = base_home_y - scale*arm_data['elbow_y'];
    let YELLOW = "#FFCC00";
    draw_line([base_home_x, base_home_y+10], [to_x1, to_y1], YELLOW)
    // draw second arm segment
    let to_x2 = base_home_x + scale*arm_data['hand_x'];
    let to_y2 = base_home_y - scale*arm_data['hand_y'];
    let RED = "#FF0000";
    draw_line([to_x1, to_y1], [to_x2, to_y2], RED)
}

function draw_initial_arm() {
    set_hand_pos(hand_home_x, hand_home_y);
    fetch('/get_arm_data').then(function(data){
        return data.json();
    }).then(function (arm_data) {
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

$("body").mousemove(function(e){handle_mouse_move(e);});
function handle_mouse_move(e) {
    let mouseX=parseInt(e.clientX-offsetX);
    let mouseY=parseInt(e.clientY-offsetY);
    const message = {'x': mouseX - base_home_x, 'y': base_home_y - mouseY};
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

function move_image(html_id, newX, newY) {
    let image = $("#" + html_id);
    image.css("left", newX + "px");
    image.css("top", newY + "px");
}

function img_error(image) {
    image.onerror = "";
    image.src = "/images/noimage.gif";
    console.log("image error");
    return true;
}