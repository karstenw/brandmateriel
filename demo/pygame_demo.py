#! /usr/env python

import sys
import numpy as np
import pygame
# import pygame.locals as l
import camera as c
import mapper as m
import shader as s
import triDobjects as o

RESOLUTION = (640, 480)

if not pygame.font:
    print "Warning: no fonts detected; fonts disabled."

if not pygame.mixer:
    print "Warning: no sound detected; sound disabled."


def do_demo(filename='demodata.npy', cam=None, look_at=None, sealevel=0):
    screen = pygame.display.set_mode(RESOLUTION, pygame.DOUBLEBUF)
    scene = m.Map(filename, sealevel)

    if cam is None:
        cam = c.Camera(position=np.array([scene.positions[:, 0].mean(),
                       -2 * np.ceil(scene.positions[:, 2].max()) - 9.0,
                       2 * np.ceil(scene.positions[:, 2].max()) + 6.0]),
                       screen=c.Screen(resolution=np.array(RESOLUTION)))

    shader = s.Shader(cam)

    if look_at is not None:
        cam.look_at_point(look_at)

    # pixels = cam.get_screen_coordinates(scene.positions)
    colours = shader.apply_lighting(scene.positions, scene.normals,
                                    scene.colours.copy())
    patches, depth = cam.get_screen_coordinates(scene.patches)

    order = np.argsort(-((scene.positions - cam.position) ** 2).mean(-1))

    for n in order:
        # Use this to render point cloud in uniform colour:
        # screen.set_at(np.round(pixels[n]).astype(np.int), (204, 0, 0))

        # Use this to render point cloud in shaded colours (not pretty):
        # screen.set_at(np.round(pixels[n]).astype(np.int), colours[n, :])

        # Use this to render patches:
        pygame.draw.polygon(screen, colours[n], patches[n])

    pygame.display.flip()

    return scene, cam


def do_live_demo(filename='demodata.npy', sealevel=7.0, steps=42, fps=30,
                 save_fig=False):
    import string
    fps_clock = pygame.time.Clock()
    screen = pygame.display.set_mode(RESOLUTION, pygame.DOUBLEBUF)

    scene = m.Map(filename, sealevel, True)
    look_at = np.array([31, 33, 21])
    cam = c.Camera(position=np.array([scene.positions[:, 0].mean(),
                   -2 * np.ceil(scene.positions[:, 2].max()) - 9.0,
                   2 * np.ceil(scene.positions[:, 2].max()) + 6.0]),
                   screen=c.Screen(resolution=np.array(RESOLUTION)))

    shader = s.Shader(cam)

    angles = np.linspace(0, 2 * np.pi, steps + 1)
    R = np.linalg.norm(cam.position[: 2] - look_at[: 2])

    for N, a in enumerate(angles):
        screen.fill((0, 0, 0))
        cam.position = np.array([np.sin(a) * R + 31, np.cos(a) * R + 33, 42])
        cam.look_at_point(look_at)

        # pixels = cam.get_screen_coordinates(scene.positions)
        colours = shader.apply_lighting(scene.positions, scene.normals,
                                        scene.colours.copy())
        patches, depth = cam.get_screen_coordinates(scene.patches)

        order = np.argsort(-((scene.positions - cam.position) ** 2).mean(-1))

        for n in order:
            # Use this to render point cloud in uniform colour:
            # screen.set_at(np.round(pixels[n]).astype(np.int), (204, 0, 0))

            # Use this to render point cloud in shaded colours (not pretty):
            # screen.set_at(np.round(pixels[n]).astype(np.int), colours[n, :])

            # Use this to render patches:
            pygame.draw.polygon(screen, colours[n], patches[n])

        pygame.display.flip()

        if save_fig:
            pygame.image.save(screen,
                              'out/{0}.png'.format(string.zfill(str(N), 2)))

        fps_clock.tick(fps)


def do_brand_demo(filename='zdata.npy', sealevel=0.0, steps=42, fps=30,
                  save_fig=False):
    import string
    fps_clock = pygame.time.Clock()
    screen = pygame.display.set_mode(RESOLUTION, pygame.DOUBLEBUF)

    scene = m.Map(filename, sealevel, True)
    look_at = np.array([63.5, 63.5, 6.0])
    cam = c.Camera(position=np.array([54.5, 63.5, 6.0]),
                   screen=c.Screen(resolution=np.array(RESOLUTION)))

    shader = s.Shader(cam)

    fighter = o.FireFighter()

    fighter.position = np.array([63.5, 63.5, 6.0])

    house = o.House()

    house.position = np.array([71, 51, 1.0])

    angles = np.linspace(0, 2 * np.pi, steps + 1)
    R = np.linalg.norm(cam.position[: 2] - look_at[: 2])

    for N, a in enumerate(angles):
        screen.fill((0, 0, 0))
        cam.position = np.array([np.sin(a) * R + 63.5,
                                 np.cos(a) * R + 63.5, 6.0])
        cam.look_at_point(look_at)

        colours = shader.apply_lighting(scene.positions, scene.normals,
                                        scene.colours.copy())

        patches, depth = cam.get_screen_coordinates(scene.patches)

        order = np.argsort(-((scene.positions - cam.position) ** 2).mean(-1))

        for n in order:
            if ((depth[n].mean() > 0 and patches[n] >= 0).any() and
                    (patches[n, :, 0] < RESOLUTION[0]).any() and
                    (patches[n, :, 1] < RESOLUTION[1]).any()):

                pygame.draw.polygon(screen, colours[n], patches[n])

        colours = shader.apply_lighting(fighter.positions, fighter.normals,
                                        fighter.colours.copy())

        patches, depth = cam.get_screen_coordinates(fighter.patches)

        order = np.argsort(-((fighter.positions - cam.position) ** 2).mean(-1))

        for n in order:
            if (colours[n, 3] and depth[n].mean() > 0 and
                    (patches[n] >= 0).any() and
                    (patches[n, :, 0] < RESOLUTION[0]).any() and
                    (patches[n, :, 1] < RESOLUTION[1]).any()):
                pygame.draw.polygon(screen, colours[n], patches[n])

        colours = shader.apply_lighting(house.positions, house.normals,
                                        house.colours.copy())

        patches, depth = cam.get_screen_coordinates(house.patches)

        order = np.argsort(-((house.positions - cam.position) ** 2).mean(-1))

        for n in order:
            if (colours[n, 3] and depth[n].mean() > 0 and
                    (patches[n] >= 0).any() and
                    (patches[n, :, 0] < RESOLUTION[0]).any() and
                    (patches[n, :, 1] < RESOLUTION[1]).any()):
                pygame.draw.polygon(screen, colours[n], patches[n])

        pygame.display.flip()

        if save_fig:
            pygame.image.save(screen,
                              'out/{0}.png'.format(string.zfill(str(N), 2)))

        fps_clock.tick(fps)


def main():
    pygame.init()
    # do_demo()
    # do_live_demo(save_fig=False)
    do_brand_demo(save_fig=True)


if __name__ == "__main__":
    sys.exit(main())
