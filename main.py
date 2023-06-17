import time
import curses
import asyncio
import random

from frames.fire_animation.fire_animation import fire
from frames.rocket_animation.rocket import animate_spaceship


TIC_TIMEOUT = 0.1


class EventLoopCommand():
    def __await__(self):
        return (yield self)


class Delay(EventLoopCommand):
    def __init__(self, seconds):
        self.seconds = seconds


def get_canvas_borders(canvas):
    max_row, max_col = canvas.getmaxyx()
    return max_row - 1, max_col - 1


async def blink(canvas, row, column, symbol='*', offset=0):
    animation = [
        (40, curses.A_DIM),
        (6, curses.A_NORMAL),
        (15, curses.A_BOLD),
        (6, curses.A_NORMAL),
    ]

    await Delay(15)

    while True:
        offset = random.randint(25, 50)
        await Delay(offset)

        for delay, font in animation:
            canvas.addstr(
              row,
              column,
              symbol,
              font
            )
            await Delay(delay)


async def draw(canvas):
    curses.curs_set(False)
    canvas.border()
    canvas.refresh()
    canvas.nodelay(True)

    max_row, max_col = get_canvas_borders(canvas)
    start_row, start_column = get_canvas_borders(canvas)
    start_row = start_row // 2
    start_column = start_column // 2
    fire_coroutine = fire(canvas, start_row, start_column)
    spaceship_coroutine = animate_spaceship(canvas, start_row, start_column)
    coroutines = [fire_coroutine, spaceship_coroutine, ]

    for _ in range(0, random.randint(25, 50)):
        coroutines.append(
            blink(canvas, random.randint(0, max_row),
                  random.randint(0, max_col),
                  random.choice(['+', '*', '.', ':'])))

    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        if len(coroutines) == 0:
            break
        canvas.refresh()
        time.sleep(TIC_TIMEOUT)


def run(canvas):
    asyncio.run(draw(canvas))


def main():
    curses.wrapper(run)


if __name__ == "__main__":
    main()
