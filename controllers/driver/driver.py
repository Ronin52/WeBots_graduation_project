# Copyright 1996-2020 Cyberbotics Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This controller gives to its node the following behavior:
Listen the keyboard. According to the pressed key, send a
message through an emitter or handle the position of Robot1.
"""

from controller import Supervisor


class Driver (Supervisor):
    timeStep = 128

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
