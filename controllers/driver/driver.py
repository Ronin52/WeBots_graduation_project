from controller import Supervisor


class Driver(Supervisor):
    timeStep = 32

    def __init__(self):
        super(Driver, self).__init__()
        self.emitter = self.getEmitter('emitter')
        self.keyboard.enable(Driver.timeStep)
        self.keyboard = self.getKeyboard()

    def run(self):
        previous_message = ''

        while True:
            k = self.keyboard.getKey()
            message = ''
            if k == ord('W'):
                message = 'W'
            elif k == ord('A'):
                message = 'A'
            elif k == ord('S'):
                message = 'S'
            elif k == ord('D'):
                message = 'D'
            elif k == ord(' '):
                message = 'STOP'
            elif k == ord('1'):
                message = "1"
            elif k == ord('2'):
                message = "2"
            elif k == ord('3'):
                message = "3"
            elif k == ord('4'):
                message = "4"
            elif k == ord('5'):
                message = "5"
            elif k == ord('6'):
                message = "6"
            elif k == ord('7'):
                message = "7"
            elif k == ord('8'):
                message = "8"
            elif k == ord('9'):
                message = "9"
            elif k == ord('0'):
                message = "0"
            elif k == ord('M'):
                message = "AUTO"

            if message != '' and message != previous_message:
                previous_message = message
                print("I SAY " + message)
                self.emitter.send(message.encode('utf-8'))

            if self.step(self.timeStep) == -1:
                break


controller = Driver()
controller.run()
