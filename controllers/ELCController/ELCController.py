from controller import Robot

import time

# Константы
# Максимальное значение передних датчиков
FRONT_DISTANCE_SENSOR_MIN_VALUE = 70
# Максимальное значение боковых данчиков
SIDE_DISTANCE_SENSOR_MIN_VALUE = 70
#
DISTANCE_SENSOR_MAX_VALUE = 200
# Соответсвие списка значений с датчиков по индексу
LB = 0
LF = 1
FL = 2
FC = 3
FR = 4
RF = 5
RB = 6


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
        self.left_ps.enable(self.time_step)
        self.right_ps.enable(self.time_step)
        self.ds_fc.enable(self.time_step)
        self.ds_fl.enable(self.time_step)
        self.ds_fr.enable(self.time_step)
        self.ds_lf.enable(self.time_step)
        self.ds_lb.enable(self.time_step)
        self.ds_rf.enable(self.time_step)
        self.ds_rb.enable(self.time_step)
        self.receiver.enable(self.time_step)


class Settings:
    message = "STOP"
    prev_message = "STOP"
    speed = 0
    auto_move = False
    block_forward = False
    inner_turn_mode = 0
    divide_deviation = 0.17
    end_wall = False
    outer_turn_mode = 0
    counter = 100
    in_outer_turn = False
    outer_turn_completed = False
    ps_left_old = 0
    ps_right_old = 0


elc_bot = ELCBot()
settings = Settings()


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
    return ds_values[FL] < FRONT_DISTANCE_SENSOR_MIN_VALUE or \
           ds_values[FC] < FRONT_DISTANCE_SENSOR_MIN_VALUE or \
           ds_values[FR] < FRONT_DISTANCE_SENSOR_MIN_VALUE


def left_obstacle():
    global ds_values
    return ds_values[LF] < SIDE_DISTANCE_SENSOR_MIN_VALUE or \
           ds_values[LB] < SIDE_DISTANCE_SENSOR_MIN_VALUE


def right_obstacle():
    global ds_values
    return ds_values[RF] < SIDE_DISTANCE_SENSOR_MIN_VALUE or \
           ds_values[RB] < SIDE_DISTANCE_SENSOR_MIN_VALUE


def left_equal():
    global ds_values
    return abs(ds_values[LF] - ds_values[LB]) <= settings.divide_deviation


def right_equal():
    global ds_values
    return abs(ds_values[RF] - ds_values[RB]) <= settings.divide_deviation


def get_outer_turn_mode():
    global ds_values
    if ds_values[RB] <= SIDE_DISTANCE_SENSOR_MIN_VALUE and ds_values[RF] > DISTANCE_SENSOR_MAX_VALUE:
        return 1
    if ds_values[LB] <= SIDE_DISTANCE_SENSOR_MIN_VALUE and ds_values[LF] > DISTANCE_SENSOR_MAX_VALUE:
        return -1
    return 0


def turn_90():
    global ps_values
    return abs(ps_values[0] - ps_values[1]) >= 12.5


def complete_turn_90():
    global settings, ps_values
    print(ps_values[0], ps_values[1])
    settings.ps_left_old = ps_values[0]
    settings.ps_right_old = ps_values[1]

"""
Нам нужно какое то действие по умолчанию.
В движении вдоль отбойника это собственно движение вперед, оно по умолчанию, а угол поворота колес задается пид
В детектировании препятсвий это движение вдоль линии, и если препятсятвие мешает объезжаем его и двигаемся опять
В нашем случае движение по умолчанию какое?
Окай, если движение вперед, то у нас может быть первоначальная ситуация, когда у робота нет стены рядом 
и у нас нет угла поворота у нас есть просто поворот, тогда он будет крутиться на месте
Самая оптимальная для нас стратегия это из лабы с обходом лабиринта:
Едем вперед.
Впереди препятствие.
Приоритет поворота - направо
Если справа нет препятствия - запускаем сценарий поворота направо на 90 градусов и разрежаем движение вперед
Если справа есть, а слева нет - запускаем поворот налево на 90 градусов и разрежаем движение вперед
Еще надо обработать условие, когда мы теряем направляющую стену, тогда мы должны проехать чутка вперед и развернуться
И все это делается на циклах, и if
Другого варианта я не вижу, потому что программа выполняется иттерационно и каждую итерацию должно быть какие то
проверки которые соответсвенно менают какие то данные
В общем тут как то все не тривиально и в целом капец. Я реально в отчаянии нужна помощь.
"""

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
            # PID вдоль стены
            # Обход периметра по часовой стрелке
            # с минимальным расстоянием от стены
            # Внешний угол - PID + поворот за угол
            # Внутренний угол - обход препятствий + поворот на 90
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

        ps_values = [elc_bot.left_ps.getValue() - settings.ps_left_old,
                     elc_bot.right_ps.getValue() - settings.ps_right_old]

        if not settings.block_forward:
            if front_obstacle():
                print("1 block forward")
                settings.block_forward = True
                continue
            if get_outer_turn_mode() != 0:
                print("1.1 end wall")
                settings.block_forward = True
                settings.end_wall = True
                settings.outer_turn_mode = get_outer_turn_mode()
                continue
            if not front_obstacle():
                settings.speed = 10
                move_forward()
                continue
        if settings.block_forward:
            if not settings.end_wall:
                if settings.inner_turn_mode == 0:
                    if not left_obstacle():
                        print("3 left clear")
                        settings.inner_turn_mode = -1
                        settings.speed = 2
                        turn_left()
                        continue
                    if not right_obstacle():
                        print("2 right clear")
                        settings.inner_turn_mode = 1
                        settings.speed = 2
                        turn_right()
                        continue
                if right_equal() and settings.inner_turn_mode == -1 and right_obstacle():
                    print("4 stop turn")
                    settings.inner_turn_mode = 0
                    settings.block_forward = False
                    complete_turn_90()
                    stop()
                    continue

                if left_equal() and settings.inner_turn_mode == 1 and left_obstacle():
                    print("5 stop turn")
                    settings.inner_turn_mode = 0
                    settings.block_forward = False
                    complete_turn_90()
                    stop()
                    continue
            if settings.end_wall:
                if not settings.in_outer_turn:
                    settings.speed = 2
                    move_forward()
                if settings.outer_turn_mode == 1:
                    if not right_obstacle():
                        if settings.counter > 0:
                            settings.counter -= 1
                            continue
                        if settings.counter == 0:
                            settings.in_outer_turn = True
                            turn_right()
                        if settings.in_outer_turn and turn_90():
                            print("im here")
                            complete_turn_90()
                            settings.in_outer_turn = False
                            settings.counter = 100
                            settings.block_forward = False
                            settings.end_wall = False
                            continue
                if settings.outer_turn_mode == -1:
                    if not left_obstacle():
                        if settings.counter > 0:
                            settings.counter -= 1
                            continue
                        if settings.counter == 0:
                            settings.in_outer_turn = True

                            turn_left()
                        if settings.in_outer_turn and turn_90():
                            print("im here")
                            complete_turn_90()
                            settings.in_outer_turn = False
                            settings.counter = 100
                            settings.block_forward = False
                            settings.end_wall = False
                            continue

    pass
