import discord
import car


class ConnectFourGame(object):
    def __init__(self, bot, *, width=7, height=6, icon1="🔴", icon2="🟡"):
        self._board = [[None for _ in range(height)] for _ in range(width)]
        self._current_player = 0
        self._icon1 = icon1
        self._icon2 = icon2
        self._width = width
        self._height = height

        self.players = []

    def __str__(self):
        s = ""
        for i in range(self._height):
            for j in range(self._width):
                s += self._board[i][j]

            s += "\n"

    def switch_turns(self):
        self._player_toggle ^= 1

    def move(self, col):
        if pos < 1 or pos > width:
            raise car.ArgumentError(f"This must be from 1 to {width}!")

        for i in range(height, -1, -1):
            if i == 0:
                raise car.ArgumentError(f"This column is full!")

            if self._board[col][i] is None:
                self._board[col][i] = self._current_player
                break

    def get_winner(self):
        for i in range(self._width-3):
            for j in range(self._height-3):
                if self._board[i][j] is None:
                    continue
                if self._board[i][j] == self._board[i+1][j+1] \
                        == self._board[i+2][j+2] == self._board[i+3][j+3]:
                    return self._board[i][j]

                if self._board[i+3][j] is None:
                    continue
                if self._board[i+3][j] == self._board[i+2][j+1] \
                        == self._board[i+1][j+2] == self._board[i][j+3]:
                    return self._board[i][j+3]

        for i in range(self._width-3):
            for j in range(self._height):
                if self._board[i][j] is None:
                    continue
                if self._board[i][j] == self._board[i+1][j] \
                        == self._board[i+2][j] == self._board[i+3][j]:
                    return self._board[i][j]

        for i in range(self._width):
            for j in range(self._height-3):
                if self._board[i][j] is None:
                    continue
                if self._board[i][j] == self._board[i][j+1] \
                        == self._board[i][j+2] == self._board[i][j+3]:
                    return self._board[i][j]

        return None

    def is_full(self):
        for i in range(width):
            if self._board[width][0] is None:
                return True

        return False

class Games(car.Cog):
    def __init__(self, bot):
        super().__init__(bot, global_category="Hidden")
        self.cf_boards = {}

    @car.command()
    async def cf(self, ctx, member: car.to_member() = None):
        """
        Creates a Connect Four game

        If `(member)` is specified, only `(member)` can join your game
        If `(member)` already has a game, you will join `(member)`'s game
        """
        if ctx.author.id in self.cf_boards:
            raise car.CommandError("You are already in a game! use "
                                   f"`{ctx.prefix}cfquit` to quit")

    @car.command(aliases=["cfq"])
    async def cfquit(self, ctx):
        """
        Quits a Connect Four game
        """
        pass

    @car.command(aliases=["cfm"])
    async def cfmove(self, ctx, position: car.to_int(lower=1)):
        """
        Places a tile at a position
        """
        pass

