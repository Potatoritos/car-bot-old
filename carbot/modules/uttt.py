
class UTTTDisplay(object):
    def __init__(self):
        self.board = [
            list(".                        \n"),
            list("  - - - │ - - - │ - - -  \n"),
            list("  - - - │ - - - │ - - -  \n"),
            list("  - - - │ - - - │ - - -  \n"),
            list(" ───────┼───────┼─────── \n"),
            list("  - - - │ - - - │ - - -  \n"),
            list("  - - - │ - - - │ - - -  \n"),
            list("  - - - │ - - - │ - - -  \n"),
            list(" ───────┼───────┼─────── \n"),
            list("  - - - │ - - - │ - - -  \n"),
            list("  - - - │ - - - │ - - -  \n"),
            list("  - - - │ - - - │ - - -  \n"),
            list("                         ")
        ]

    def __str__(self):
        s = []
        for r in self.board:
            s.append(''.join(r))
        return ''.join(s)

    def fill_line(self, s, x, y, dx=1, dy=0):
        for char in s:
            self.board[y][x] = char
            x += dx
            y += dy

    def select_local(self, x, y):
        x1, y1, x2, y2 = x*8, y*4, (x+1)*8-1, (y+1)*4
        self.fill_line("┏ABC┗", x1, y1, 0, 1)
        self.fill_line("━1 2 3━", x1+1, y1)
        self.fill_line("┓┃┃┃┛", x2+1, y1, 0, 1)
        self.fill_line("━━━━━━━", x1+1, y2)

    def unselect_local(self, x, y):
        x1, y1, x2, y2 = x*8, y*4, (x+1)*8-1, (y+1)*4
        self.fill_line("┼───────┼", x1, y1)
        self.fill_line("│││", x1, y1+1, 0, 1)
        self.fill_line("┼───────┼", x1, y2)
        self.fill_line("│││", x2+1, y1+1, 0, 1)
        if x == 0:
            self.fill_line(" "*5, x1, y1, 0, 1)
        elif x == 2:
            self.fill_line(" "*5, x2+1, y1, 0, 1)
        if y == 0:
            self.fill_line(" "*9, x1, y1)
        elif y == 2:
            self.fill_line(" "*9, x1, y2)

    def select_global(self):
        self.board[0][4] = '1'
        self.board[0][12] = '2'
        self.board[0][20] = '3'
        self.board[2][0] = 'A'
        self.board[6][0] = 'B'
        self.board[10][0] = 'C'

    def unselect_global(self):
        self.board[0][4] = ' '
        self.board[0][12] = ' '
        self.board[0][20] = ' '
        self.board[2][0] = ' '
        self.board[6][0] = ' '
        self.board[10][0] = ' '

class UTTTGame(object):
    def __init__(self):
        self.display = UTTTDisplay()
        self.local_boards = [
            [
                [
                    [
                        '-' for _ in range(3)
                    ] for _ in range(3)
                ] for _ in range(3)
            ] for _ in range(3)
        ]
        self.global_board = [['-' for _ in range(3)] for _ in range(3)]
        self.turn = 'X'

    def get_winner(board):
        configs = [
            ((0,0), (1,1), (2,2)),
            ((0,2), (1,1), (0,2)),
            ((0,0), (1,0), (2,0)),
            ((0,1), (1,1), (2,1)),
            ((0,2), (1,2), (2,2)),
            ((0,0), (0,1), (0,2)),
            ((1,0), (1,1), (1,2)),
            ((2,0), (2,1), (2,2))
        ]
        for conf in configs:
            if self.board[conf[0][0]][conf[0][1]] \
                    == self.board[conf[1][0]][conf[1][1]] \
                    == self.board[conf[2][0]][conf[2][1]]:
                return (self.board[conf[0][0]][conf[0][1]], conf)
        return (None, None)

    def swap_turns(self):
        self.turn = 'X' if self.turn == 'O' else 'O'

    def move(self):
        pass



b = UTTTBoard()
print(b)
b.select_global()
print(b)
b.unselect_global()
b.select_local(1,1)
print(b)
b.unselect_local(1,1)
b.select_local(2,0)
print(b)
b.unselect_local(2,0)
print(b)
