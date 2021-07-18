# 2-Joint Arm Simulator
Uses inverse kinematics to bend arm's joints appropriately to reach cursor. Hardware design for arm is also included to be built whenever the pandemic is over. In the meantime, I built a small web app to simulate the arm.
![Alt_text](TwoJointBot/frontend/static/images/twojointarm_app_screenshot.png)
#### Setup
```console
% cd TwoJointBot  
% pipenv --three install  
% pipenv run python arm_app.py  
```
Go to url specified by output. Will look something like http://127.0.0.1:5000/
#### Acknowledgements
Mechanical design: Aidan Miller  
Render and design schematic: Murun Tsogtkhuyag  
