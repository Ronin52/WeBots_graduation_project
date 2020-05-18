from controller import Robot


class ELCBot(Robot):
    time_step = 32
    max_speed = 10.0

    def __init__(self):
        super(ELCBot, self).__init__()
        self.left_motor = self.getMotor('left_wheel_motor')
        self.right_motor = self.getMotor('right_wheel_motor')
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


elc_bot = ELCBot()

mode = "STOP"

while elc_bot.step(elc_bot.time_step) != -1:
    if elc_bot.receiver.getQueueLength() > 0:
        message = elc_bot.receiver.getData().decode('utf-8')
        elc_bot.receiver.nextPacket()
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
        elif message == 'GET':
            mode = "GET"
    if mode == "W":
        elc_bot.left_motor.setVelocity(5)
        elc_bot.right_motor.setVelocity(5)
    elif mode == "A":
        elc_bot.left_motor.setVelocity(-5)
        elc_bot.right_motor.setVelocity(5)
    elif mode == "S":
        elc_bot.left_motor.setVelocity(-5)
        elc_bot.right_motor.setVelocity(-5)
    elif mode == "D":
        elc_bot.left_motor.setVelocity(5)
        elc_bot.right_motor.setVelocity(-5)
    elif mode == "STOP":
        elc_bot.left_motor.setVelocity(0)
        elc_bot.right_motor.setVelocity(0)
    elif mode == "GET":
        print(elc_bot.ds_fc.getValue())
        mode = "STOP"
