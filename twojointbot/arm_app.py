from flask import Flask, render_template, request, jsonify
from backend.twojoint_arm import TwoJointArm

app = Flask(__name__, template_folder='frontend/templates', static_folder='frontend/static')
# dimensions of the real bot arm in cm scaled by 4
forearm_len = 52.6 * 4
bicep_len = 42 * 4
elbow_angle_limit = 175
shoulder_angle_limit = 170
arm = TwoJointArm(forearm_len, bicep_len, 10, 10,
                  shoulder_angle_limit,
                  elbow_angle_limit)
sign = -1  # elbow direction

@app.route('/', methods=['GET', 'POST'])
def index():
    """main url"""
    return render_template('arm_index.html')

@app.route('/get_arm_data', methods=['GET', 'POST'])
def get_arm_data():
    successful = 1
    if request.method == 'POST':
        json = request.get_json(force=True)
        successful = arm.move_to((json['x'], json['y']), sign)

    # elbow_above_table = arm.elbow[1] >= 0
    arm_data = {
        "bicep_length": str(arm.bicep_length),
        "forearm_length": str(arm.forearm_length),
        "elbow_x": str(arm.elbow[0]),
        "elbow_y": str(arm.elbow[1]),
        "hand_x": str(arm.hand[0]),
        "hand_y": str(arm.hand[1]),
        "bicep_angle": str(arm.bicep_angle),
        "forearm_angle": str(arm.forearm_angle),
        "successful": successful  # and elbow_above_table
    }
    return jsonify(arm_data)

if __name__ == '__main__':
    app.run(debug=True)

