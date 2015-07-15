import phenox as px

def set_parameter():
    param = px.PhenoxConfig()
    param.duty_hover = 1200
    param.duty_hover_max = 1350
    param.duty_hover_min = 1000
    param.duty_up = 1350
    param.duty_down = 1000
    param.duty_bias_front = 0
    param.duty_bias_back = 0
    param.duty_bias_left = 130
    param.duty_bias_right = -130
    param.pgain_sonar_tz = 45.0/1000.0
    param.dgain_sonar_tz = 20.0
    param.pgain_vision_tx = 0.032
    param.pgain_vision_ty = 0.032
    param.dgain_vision_tx = 0.80
    param.dgain_vision_ty = 0.80
    param.whisleborder = 280
    param.soundborder = 1000
    param.uptime_max = 0.8
    param.downtime_max = 3.0
    param.dangz_rotspeed = 15.0
    param.selxytime_max = 3
    param.featurecontrast_front = 35
    param.featurecontrast_bottom = 25
    param.pgain_degx = 880
    param.pgain_degy = 880
    param.pgain_degz = 2400
    param.dgain_degx = 22
    param.dgain_degy = 22
    param.dgain_degz = 28
    param.pwm_or_servo = 0  
    param.propeller_monitor = 1
    px.set_pconfig(param)

