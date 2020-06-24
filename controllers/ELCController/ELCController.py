from controller import Robot

import time

# Константы
# Максимальное значение передних датчиков
FRONT_DISTANCE_SENSOR_MAX_VALUE = 50
# Максимальное значение боковых данчиков
SIDE_DISTANCE_SENSOR_MAX_VALUE = 40
# Соответсвие списка значений с датчиков по индексу
LB = 0
LF = 1
FL = 2
FC = 3
FR = 4
RF = 5
RB = 6
#
DEFAULT = 0
LEFT = -1
RIGHT = 1


class ELCBot(Robot):
    time_step = 32
    max_speed = 10.0

    def __init__(self):
        super(ELCBot, self).__init__()
        self.left_motor = self.getMotor('left_wheel_motor')
        self.right_motor = self.getMotor('right_wheel_motor')
        self.left_ps = self.getPositionSensor('left_wheel_position_sensor')
        self.right_ps = self.getPositionSensor('right_wheel_position_sensor')
        self.ds_fc = self.getDistanceSensor('ds_fc')
        self.ds_fl = self.getDistanceSensor('ds_fl')
        self.ds_fr = self.getDistanceSensor('ds_fr')
        self.ds_lf = self.getDistanceSensor('ds_lf')
        self.ds_lb = self.getDistanceSensor('ds_lb')
        self.ds_rf = self.getDistanceSensor('ds_rf')
        self.ds_rb = self.getDistanceSensor('ds_rb')
        self.receiver = self.getReceiver('receiver')
        self.left_motor.setPosition(float('inf'))
        self.left_motor.setVelocity(0.0)
        self.right_motor.setPosition(float('inf'))
        self.right_motor.setVelocity(0.0)
        self.ds_fc.enable(self.time_step)
        self.ds_fl.enable(self.time_step)
        self.ds_fr.enable(self.time_step)
        self.ds_lf.enable(self.time_step)
        self.ds_lb.enable(self.time_step)
        self.ds_rf.enable(self.time_step)
        self.ds_rb.enable(self.time_step)
        self.receiver.enable(self.time_step)
        self.camera = self.getCamera('camera')
        self.camera.enable(4 * self.time_step)


class Settings:
    message = "STOP"
    prev_message = "STOP"
    speed = 0
    auto_move = False
    block_forward = False
    turn_mode = DEFAULT
    divide_deviant = 0.2
    on_wall = DEFAULT
    kd_for_wall = 0.975
    kd_for_outer_turn = 2


class PID:
    kp = 0.1
    ki = 0.022
    kd = 0.97
    integral = 0.0
    old_y = 0.0
    integral_min = -1.0
    integral__max = 1.0


elc_bot = ELCBot()
settings = Settings()
pid = PID()


def print_ds():
    global elc_bot
    print("ds_lb: ", elc_bot.ds_lb.getValue())
    print("ds_lf: ", elc_bot.ds_lf.getValue())
    print("ds_fl: ", elc_bot.ds_fl.getValue())
    print("ds_fc: ", elc_bot.ds_fc.getValue())
    print("ds_fr: ", elc_bot.ds_fr.getValue())
    print("ds_rf: ", elc_bot.ds_rf.getValue())
    print("ds_rb: ", elc_bot.ds_rb.getValue())


def stop():
    global elc_bot
    elc_bot.left_motor.setVelocity(0)
    elc_bot.right_motor.setVelocity(0)


def move_forward():
    global elc_bot
    elc_bot.left_motor.setVelocity(settings.speed)
    elc_bot.right_motor.setVelocity(settings.speed)


def move_backward():
    global elc_bot
    elc_bot.left_motor.setVelocity(-settings.speed)
    elc_bot.right_motor.setVelocity(-settings.speed)


def turn_left():
    global elc_bot
    elc_bot.left_motor.setVelocity(-settings.speed)
    elc_bot.right_motor.setVelocity(settings.speed)


def turn_right():
    global elc_bot
    elc_bot.left_motor.setVelocity(settings.speed)
    elc_bot.right_motor.setVelocity(-settings.speed)


def speed_handler():
    global elc_bot, settings

    def set_speed(new_speed):
        print('MY SPEED = ', new_speed, '!')
        settings.speed = new_speed
        settings.message = settings.prev_message

    if settings.message == "1":
        set_speed(1)
    elif settings.message == "2":
        set_speed(2)
    elif settings.message == "3":
        set_speed(3)
    elif settings.message == "4":
        set_speed(4)
    elif settings.message == "5":
        set_speed(5)
    elif settings.message == "6":
        set_speed(6)
    elif settings.message == "7":
        set_speed(7)
    elif settings.message == "8":
        set_speed(8)
    elif settings.message == "9":
        set_speed(9)
    elif settings.message == "0":
        set_speed(10)


def velocity_handler():
    global settings
    if settings.message == 'W':
        print('I MOVE FORWARD!')
        move_forward()
    elif settings.message == 'A':
        print('I TURN LEFT!')
        turn_left()
    elif settings.message == 'S':
        print('I MOVE BACKWARD!')
        move_backward()
    elif settings.message == 'D':
        print('I TURN RIGHT!')
        turn_right()
    elif settings.message == 'STOP':
        print('I STOP!')
        stop()


def front_obstacle():
    global ds_values
    return ds_values[FL] < FRONT_DISTANCE_SENSOR_MAX_VALUE or \
           ds_values[FC] < FRONT_DISTANCE_SENSOR_MAX_VALUE or \
           ds_values[FR] < FRONT_DISTANCE_SENSOR_MAX_VALUE


def left_obstacle():
    global ds_values
    return ds_values[LF] < SIDE_DISTANCE_SENSOR_MAX_VALUE or \
           ds_values[LB] < SIDE_DISTANCE_SENSOR_MAX_VALUE


def right_obstacle():
    global ds_values
    return ds_values[RF] < SIDE_DISTANCE_SENSOR_MAX_VALUE or \
           ds_values[RB] < SIDE_DISTANCE_SENSOR_MAX_VALUE


def left_equal():
    global ds_values
    return abs(ds_values[LF] - ds_values[LB]) <= settings.divide_deviant


def right_equal():
    global ds_values
    return abs(ds_values[RF] - ds_values[RB]) <= settings.divide_deviant


def end_wall():
    global ds_values
    if ds_values[RF] > SIDE_DISTANCE_SENSOR_MAX_VALUE + 20 >= ds_values[RB]:
        return RIGHT
    if ds_values[LF] > SIDE_DISTANCE_SENSOR_MAX_VALUE >= ds_values[LB]:
        return LEFT
    return DEFAULT


def evaluate_pid(distance):
    global pid
    error = distance - SIDE_DISTANCE_SENSOR_MAX_VALUE

    up = pid.kp * error

    pid.integral -= error
    if pid.integral > pid.integral__max:
        pid.integral = pid.integral__max
    else:
        if pid.integral < pid.integral_min:
            pid.integral = pid.integral_min
    ui = pid.ki * pid.integral

    ud = pid.kd * error - pid.old_y
    us = up + ui + ud
    pid.old_y = error
    if us >= 10:
        us = 10
    if us <= -10:
        us = -10
    return us


while elc_bot.step(elc_bot.time_step) != -1:
    if elc_bot.receiver.getQueueLength() > 0:
        settings.prev_message = settings.message
        settings.message = elc_bot.receiver.getData().decode('utf-8')
        elc_bot.receiver.nextPacket()
        settings.auto_move = False

        speed_handler()
        velocity_handler()

        if settings.message == "PRINT":
            print_ds()
            settings.message = settings.prev_message
        if settings.message == "AUTO":
            print("AUTO MOVE MODE!")
            settings.auto_move = True
    if settings.auto_move:
        ds_values = [elc_bot.ds_lb.getValue(),
                     elc_bot.ds_lf.getValue(),
                     elc_bot.ds_fl.getValue(),
                     elc_bot.ds_fc.getValue(),
                     elc_bot.ds_fr.getValue(),
                     elc_bot.ds_rf.getValue(),
                     elc_bot.ds_rb.getValue()]

        if not settings.block_forward:
            if front_obstacle():
                settings.block_forward = True
                continue

            if settings.on_wall == DEFAULT:
                if not front_obstacle():
                    if right_obstacle():
                        pid.kd = settings.kd_for_wall
                        settings.on_wall = RIGHT
                        continue
                    if left_obstacle():
                        pid.kd = settings.kd_for_wall
                        settings.on_wall = LEFT
                        continue
                    settings.speed = 10
                    move_forward()
                    continue

            if settings.on_wall == RIGHT:
                if end_wall() == RIGHT:
                    pid.kd = settings.kd_for_outer_turn
                if end_wall() == DEFAULT:
                    pid.kd = settings.kd_for_wall
                settings.speed = 10
                u = evaluate_pid(ds_values[RF])
                if u < 0:
                    elc_bot.left_motor.setVelocity(settings.speed - abs(u))
                    elc_bot.right_motor.setVelocity(settings.speed)
                if u > 0:
                    elc_bot.left_motor.setVelocity(settings.speed)
                    elc_bot.right_motor.setVelocity(settings.speed - abs(u))
                if u == 0:
                    elc_bot.left_motor.setVelocity(settings.speed)
                    elc_bot.right_motor.setVelocity(settings.speed)
            if settings.on_wall == LEFT:
                settings.speed = 10
                u = evaluate_pid(ds_values[LF])
                if u < 0:
                    elc_bot.left_motor.setVelocity(settings.speed)
                    elc_bot.right_motor.setVelocity(settings.speed - abs(u))
                if u > 0:
                    elc_bot.left_motor.setVelocity(settings.speed - abs(u))
                    elc_bot.right_motor.setVelocity(settings.speed)
                if u == 0:
                    elc_bot.left_motor.setVelocity(settings.speed)
                    elc_bot.right_motor.setVelocity(settings.speed)

        if settings.block_forward:
            if settings.turn_mode == DEFAULT:

                if not left_obstacle():
                    settings.turn_mode = LEFT
                    settings.speed = 2
                    turn_left()
                    continue

                if not right_obstacle():
                    settings.turn_mode = RIGHT
                    settings.speed = 2
                    turn_right()
                    continue

            if right_equal() and settings.turn_mode == LEFT and right_obstacle():
                settings.turn_mode = DEFAULT
                settings.block_forward = False
                settings.on_wall = RIGHT
                stop()
                continue

            if left_equal() and settings.turn_mode == RIGHT and left_obstacle():
                settings.turn_mode = DEFAULT
                settings.block_forward = False
                settings.on_wall = LEFT
                stop()
                continue

    pass
