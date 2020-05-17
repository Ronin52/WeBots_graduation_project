from controller import Robot, Motor

TIME_STEP = 32

robot = Robot()
motor1 = robot.getMotor("leftWheel")
motor2 = robot.getMotor("rightWheel")
motor1.setPosition(float("inf"))
motor2.setPosition(float("inf"))
receiver = robot.getReceiver('receiver')
receiver.enable(TIME_STEP)
mode = "STOP"

while robot.step(TIME_STEP) != -1:
    if receiver.getQueueLength() > 0:
        message = receiver.getData().decode('utf-8')
        receiver.nextPacket()
        print('I DO ' + message + '!')
        if message == 'W':
            mode = "W"
        elif message == 'A':
            mode = "A"
        elif message == 'S':
            mode = "S"
        elif message == 'D':
            mode = "D"
        elif message == 'STOP':
            mode = "STOP"
    if mode == "W":
        motor1.setVelocity(5)
        motor2.setVelocity(5)
    elif mode == "A":
        motor1.setVelocity(-5)
        motor2.setVelocity(5)
    elif mode == "S":
        motor1.setVelocity(-5)
        motor2.setVelocity(-5)
    elif mode == "D":
        motor1.setVelocity(5)
        motor2.setVelocity(-5)
    elif mode == "STOP":
        motor1.setVelocity(0)
        motor2.setVelocity(0)
    