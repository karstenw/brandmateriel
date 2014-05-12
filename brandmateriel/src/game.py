# TODO:
# A lot of things can be stolen from pygame_demo.py, but implemented in better
# ways...
import numpy as np
import pygame
from pygame import locals as l
import engine as e

KEYBOARD = {l.K_UP: 'up', l.K_k: 'up', l.K_w: 'up',
            l.K_DOWN: 'down', l.K_j: 'down', l.K_s: 'down',
            l.K_LEFT: 'left', l.K_h: 'left', l.K_a: 'left',
            l.K_RIGHT: 'right', l.K_l: 'right', l.K_d: 'right',
            l.K_RETURN: 'start', l.K_SPACE: 'start',
            l.K_ESCAPE: 'quit', l.K_F1: 'help'}


class Game(object):
    """
    Here be docstring.
    """

    X = U = 0
    Y = V = 1
    Z = W = 2

    def __init__(self, config, world):
        self._config = config

        self.world = e.mapper.Map(world)

        self.player = e.mobs.Movable(e.triDobjects.FireFighter())
        self.player.position = (np.array([64, 64, 3]))

        self._populate_world()

        self.camera = e.camera.Camera(screen=
            e.camera.Screen(resolution=config["resolution"]))

        if config["camera"] == "rear":
            self.update_camera = self.update_rear_camera
        else:
            self.update_camera = self.update_fixed_camera

        self.light_source = e.shader.LightSource()

        self.shader = e.shader.Shader(self.light_source)

        self.update_camera()

    @property
    def config(self):
        return self._config

    @config.setter
    def config(self, val):
        self._config = val

    @property
    def focus_position(self):
        return self.player.position

    @property
    def _view(self):
        return self._config["view"]

    def update_fixed_camera(self):
        # Something is missing here for Z value:
        offset = np.array([0, self._view[self.Y] / 2.0 + 9.0, -1.5])

        self.camera.position = self.focus_position - offset

        self.camera.position[self.Z] = max(self.camera.position[self.Z], 6.0)

        self.light_source.position = self.camera.position + np.array([0, 0, 3])

    def update_rear_camera(self):
        # Something is missing here for Z value:
        look_at = self.focus_position.copy()
        look_at[self.Z] = max(look_at[self.Z], 6.0)
        offset = np.array([0, self._view[self.Y] / 2.0 + 9.0, -1.5])

        self.camera.position = self.focus_position - offset

        self.camera.look_at_point(look_at)

        self.light_source.position = self.camera.position + np.array([0, 0, 3])

    def _populate_world(self):
        pass

    def close_game(self):
        """ Close game. """

        return "quit"

    def return_to_menu(self):
        """ Close game. """

        return "menu"

    def handle_inputs(self):
        """ Should later handle inputs from user. """
        flag = "game"

        for event in pygame.event.get():

            if event.type == l.QUIT:

                flag = self.close_game()

            elif event.type == l.KEYDOWN and event.key in KEYBOARD.keys():

                if KEYBOARD[event.key] == 'quit':

                    flag = self.return_to_menu()

                elif KEYBOARD[event.key] == 'up':

                    self.player.pitch = min(self.player.pitch + np.pi / 24,
                                            np.pi / 2)

                elif KEYBOARD[event.key] == 'down':

                    self.player.pitch = max(self.player.pitch - np.pi / 24,
                                            -np.pi / 2)

                elif KEYBOARD[event.key] == 'left':

                    self.player.yaw = ((self.player.yaw + np.pi / 24) %
                                       (2 * np.pi))

                elif KEYBOARD[event.key] == 'right':

                    self.player.yaw = ((self.player.yaw - np.pi / 24) %
                                       (2 * np.pi))

                else:

                    pass
                    # flag = self._relay_input(event.key)

        return flag
        pass

    def do_step(self, surface):
        self.handle_inputs()

        self.player.move()

        self.player.impose_boundary_conditions(self.world)

        self.update_camera()

        # get map in view:
        map_positions = self.world.positions_list(self.focus_position,
                                                  self._view)
        map_normals = self.world.normals_list(self.focus_position, self._view)
        map_colours = self.world.colours_list(self.focus_position, self._view)
        map_patches, map_depths = self.camera.get_screen_coordinates(
            self.world.patches_list(self.focus_position, self._view))

        # get objects in view:
        pass

        # get player:
        player_positions = self.player.model.positions
        player_normals = self.player.model.normals
        player_colours = self.player.model.colours
        player_patches, player_depth = self.camera.get_screen_coordinates(
            self.player.model.patches)

        # aggregate object data:
        positions = np.r_[map_positions, player_positions]
        patches = list(map_patches[:])
        patches.extend(list(player_patches[:]))
        normals = np.r_[map_normals, player_normals]
        colours = np.r_[map_colours, player_colours]

        # impose view boundaries:
        pass

        # apply shading
        colours = self.shader.apply_lighting(positions, normals, colours)

        # sort patches
        order = np.argsort(-((positions - self.camera.position) ** 2).mean(-1))

        # draw
        surface.fill((0, 0, 0))

        for n in order:
            if colours[n, 3]:
                pygame.draw.polygon(surface, colours[n], patches[n])

        self.handle_inputs()

        return "game"
