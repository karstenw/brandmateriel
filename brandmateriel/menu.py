#! /usr/bin/env python

# Meny TODO:
# * Simple cursor movement in pygame
# DONE Extendable menu items.
# DONE navigate between submenus
# * Let menu do something:
#   - DONE cameratype: fixed or follow
#   - DONE resolution: 320x240(256), 640x480(512), 800x600(640)
#   - DONE view
#   - DONE (well... sort of) mixer levels
#   - DONE map
#   - show models
#   - show credits
#   - show high-scores
#   - start
#   - DONE exit
# * DONE Resize window based on resolution.
# * Read options from file and parse correctly
# * DONE Save options on exit and/or start
# * exit dialog
# * remove print statements
# * Fancy background stuff.

import sys
import json
import pygame
import pygame.locals as l


KEYBOARD = {l.K_UP: 'up', l.K_k: 'up', l.K_w: 'up',
            l.K_DOWN: 'down', l.K_j: 'down', l.K_s: 'down',
            l.K_LEFT: 'left', l.K_h: 'left', l.K_a: 'left',
            l.K_RIGHT: 'right', l.K_l: 'right', l.K_d: 'right',
            l.K_RETURN: 'start', l.K_SPACE: 'start',
            l.K_ESCAPE: 'quit', l.K_F1: 'help'}

if not pygame.font:
    print "Warning: no fonts detected; fonts disabled."

if not pygame.mixer:
    print "Warning: no sound detected; sound disabled."


class Menu(object):
    """
    A simple menu class, configured using JSON.
    """

    def __init__(self, _structure='menu.conf', options='user.conf'):
        self._item = 0
        self.menu = "main menu"

        with open(_structure, 'r') as f:
            self._structure = json.load(f)

        try:
            with open(options, 'r') as f:
                self.options = json.load(f)
        except IOError:
            print "Loading default settings..."
            with open("default.conf", 'r') as f:
                self.options = json.load(f)

        self._set_options()

    @property
    def _items(self):
        return len(self._structure[self.menu]['items'])

    @property
    def item(self):
        return self._structure[self.menu]["items"][self._item]

    @property
    def resolution(self):
        return tuple(self.options["resolution"])

    def _set_options(self):

        for o in self.options.keys():

            for n, item in enumerate(self._structure["options"]["items"]):

                if item[0] == o:

                    break

            if self._structure["options"]["items"][n][1][0] == "toggle":

                self._structure["options"]["items"][n][1][1] = int(
                    self.options[o])

            elif self._structure["options"]["items"][n][1][0] == "list":

                for m, l in enumerate(self._structure["options"
                                                      ]["items"][n][1][2]):
                    if l == self.options[o]:

                        self._structure["options"]["items"][n][1][1] = m

    def _save_settings(self):

        for o in self.options.keys():

            for n, item in enumerate(self._structure["options"]["items"]):

                if item[0] == o:

                    break

            if self._structure["options"]["items"][n][1][0] == "toggle":
                print o, "toggle"

                self.options[o] = (1 == self._structure["options"
                                                        ]["items"][n][1][1])

            elif self._structure["options"]["items"][n][1][0] == "list":
                print o, "list"

                self.options[o] = self._structure["options"]["items"][n][1][2][
                    self._structure["options"]["items"][n][1][1]]

            else:
                print o

        with open("user.conf", 'w') as f:
            json.dump(self.options, f)

    def close(self):
        """ Close game. """

        print "Quitting game..."

        self._save_settings()

        pygame.quit()

        return False

    def menu_navigation(self):
        """ Should later handle inputs from user. """
        flag = True

        for event in pygame.event.get():

            if event.type == l.QUIT:

                flag = self.close() and flag

            elif event.type == l.KEYDOWN:

                if KEYBOARD[event.key] == 'quit':

                    flag = self.close() and flag

                elif KEYBOARD[event.key] == 'up':

                    self._item = (self._item - 1) % self._items

                elif KEYBOARD[event.key] == 'down':

                    self._item = (self._item + 1) % self._items

                else:

                    self._relay_input(event.key)

                print "{0}: {1} {2}".format(self.menu, self._item, self.item)

        return flag

    def _relay_input(self, event_key):
        if event_key in KEYBOARD.keys():

            print "Key pressed: {0} ({1})".format(KEYBOARD[event_key],
                                                  str(event_key))
            if KEYBOARD[event_key] == 'start':

                if self.item[1][0] == 'start':

                    pass

                elif self.item[1][0] == 'quit':

                    pass

                elif self.item[1][0] == 'hiscore':

                    print "hiscore not implemented yet."

                elif self.item[1][0] == 'gallery':

                    print "gallery not implemented yet."

                elif self.item[1][0] == 'credits':

                    print "credits not implemented yet."

                elif self.item[1][0] == 'menu':

                    self.menu = self.item[1][1]
                    self._item = 0

                elif self.item[1][0] == "toggle":
                    self.item[1][1] = (self.item[1][1] + 1) % 2

                elif self.item[1][0] == "list":
                    self.item[1][1] = ((self.item[1][1] + 1) %
                                       len(self.item[1][2]))

            elif KEYBOARD[event_key] == 'left':

                if self.item[1][0] == "toggle":
                    self.item[1][1] = (self.item[1][1] - 1) % 2

                elif self.item[1][0] == "list":
                    self.item[1][1] = ((self.item[1][1] - 1) %
                                       len(self.item[1][2]))

            elif KEYBOARD[event_key] == 'right':

                if self.item[1][0] == "toggle":
                    self.item[1][1] = (self.item[1][1] + 1) % 2

                elif self.item[1][0] == "list":
                    self.item[1][1] = ((self.item[1][1] + 1) %
                                       len(self.item[1][2]))

            self._save_settings()

        else:

            print "Unknown key pressed. ({0})".format(str(event_key))

        return True


def main():
    gui = Menu('menu.conf', 'user.conf')
    pygame.init()
    fps_clock = pygame.time.Clock()
    fps = 30
    window = pygame.display.set_mode((640, 480), pygame.DOUBLEBUF)
    while(gui.menu_navigation()):
        if gui.resolution != window.get_size():
            window = pygame.display.set_mode(gui.resolution, pygame.DOUBLEBUF)
        pygame.display.flip()
        fps_clock.tick(fps)

if __name__ == "__main__":
    sys.exit(main())
