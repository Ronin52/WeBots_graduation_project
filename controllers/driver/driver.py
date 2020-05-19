from controller import Supervisor


class Driver(Supervisor):
    timeStep = 32

    def __init__(self):
        super(Driver, self).__init__()
        self.emitter = self.getEmitter('emitter')
        self.keyboard.enable(Driver.timeStep)
        self.keyboard = self.getKeyboard()

    def run(self):
        self.displayHelp()
        previous_message = ''

        # Main loop.
        while True:
            # Deal with the pressed keyboard key.
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

            # Send a new message through the emitter device.
            if message != '' and message != previous_message:
                previous_message = message
                print("I SAY " + message)
                self.emitter.send(message.encode('utf-8'))

            # Perform a simulation step, quit the loop when
            # Webots is about to quit.
            if self.step(self.timeStep) == -1:
                break

    def displayHelp(self):
        print(
            'Commands:\n'
            ' W for turn forward\n'
            ' A for turn left\n'
            ' S for turn backward\n'
            ' D for turn right\n'
            ' SPACE for stop'
        )


controller = Driver()
controller.run()
