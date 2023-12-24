import pygame
import copy
import sys
import threading

try:
    import thread
except ImportError:
    import _thread as thread
    
from time import sleep
from math import sin, cos, pi as PI

ROBOT_AMOUNT = 5
BEACON_AMOUNT = 5
BEACON_LOCATIONS = ((0,6,-6), (6,-6, 0), (0,0,0), (6,0,-6), (-6,0,6))
TIME_MAX = 200
TEAM1_INIT_LOC = [0,-6,6]
TEAM2_INIT_LOC = [-6,6,0]
#robot = [a, b, c]
#beacons = [[[x,y,z], [x,y,z], ... ], [t1, t2, ... ]]

# sizes
SIZE_X, SIZE_Y = 800,800
HEX_SIZE = 30
#colors
BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255,0,0)
BLUE = (0,0,255)
GREEN = (0,255,0)
TEAM_COLORS = (BLACK, RED, BLUE)
#------
sq3 = 3 ** 0.5 / 2
HEX_COORDS = [ [1, 0], [0.5, -sq3], [-0.5, -sq3], [-1, 0], [-0.5, sq3], [0.5, sq3] ]
HEX_COORDS = tuple(map(lambda x: (x[0] * HEX_SIZE, x[1] * HEX_SIZE), HEX_COORDS))
MAP_SIZE = 6

Fake_interrupt = False

def quit_function(fn_name):
    print("Exceeded timeout!")
    global Fake_interrupt
    thread.interrupt_main() # raises KeyboardInterrupt
    Fake_interrupt = True

def exit_after(s):
    '''
    use as decorator to exit process if 
    function takes longer than s seconds
    '''
    def outer(fn):
        def inner(*args, **kwargs):
            timer = threading.Timer(s, quit_function, args=[fn.__name__])
            timer.start()
            try:
                result = fn(*args, **kwargs)
            finally:
                timer.cancel()
            return result
        return inner
    return outer


def GameInit():
    robots1 = [copy.deepcopy(TEAM1_INIT_LOC) for i in range(ROBOT_AMOUNT)]
    robots2 = [copy.deepcopy(TEAM2_INIT_LOC) for i in range(ROBOT_AMOUNT)]
    beacons = [BEACON_LOCATIONS, [0 for i in range(BEACON_AMOUNT)]]
    scores = [0, 0]
    timeRemain = [TIME_MAX]
    gamehistory = []
    gamehistory.append(copy.deepcopy([robots1, robots2, beacons, scores, timeRemain]))
    return [robots1, robots2, beacons, scores, timeRemain, gamehistory]   
    
def VerifyOut(moves):
    defaultReturn = [[0,0,0] for i in range(ROBOT_AMOUNT)] 
    if type(moves) != list and type(moves) != tuple:
        return defaultReturn
    if len(moves) != ROBOT_AMOUNT:
        return defaultReturn
    for i in range(ROBOT_AMOUNT):
        if type(moves[i]) != list or len(moves[i]) != 3:
            moves[i] = [0,0,0]
        for x in moves[i]:
            if type(x) != int:
                moves[i] = [0,0,0]
                break
        if moves[i] != [0,0,0] and not ((0 in moves[i]) and (1 in moves[i]) and (-1 in moves[i])):
            moves[i] = [0,0,0]

def ApplyMoves(robots, moves):
    for i in range(ROBOT_AMOUNT):
        oldrobot = copy.deepcopy(robots[i])
        for j in range(3):
            robots[i][j] += moves[i][j]
        if calcDistance((0,0,0), robots[i]) > MAP_SIZE:
            robots[i] = oldrobot
    
def SwitchBeacons(beacons, robots1, robots2):
    beacon_count = [0 for i in range(BEACON_AMOUNT)]
    for data in [[robots1, 1], [robots2, -1]]:
        for robot in data[0]:
            try:
                beacon_count[beacons[0].index(tuple(robot))] += data[1]
            except ValueError:
                pass
    
    for i in range(BEACON_AMOUNT):
        if beacon_count[i] > 0:
            beacons[1][i] = 1
        if beacon_count[i] < 0:
            beacons[1][i] = 2

def ApplyScore(beacons, scores):
    for i in beacons[1]:
        if i > 0:
            scores[i - 1] += 1

def PlayGame(f1, f2):
    global Fake_interrupt
    robots1, robots2, beacons, scores, timeRemain, gamehistory = GameInit()
    dict1 = None
    dict2 = None
    f = [f1, f2]
    while timeRemain[0] != 0:
        robotsMoves = [None, None]
        for i in range(2):
            try:
                robotsMoves[i] = f[i](i+1, robots1, robots2, beacons, scores, timeRemain)
            except KeyboardInterrupt:
                if Fake_interrupt:
                    robotsMoves[i] = [[0,0,0] for i in range(ROBOT_AMOUNT)]
                    Fake_interrupt = False
                else:
                    exit()
        robots1Moves, robots2Moves = robotsMoves
        '''
        try:
            robots2Moves = f2(2, robots1, robots2, beacons, scores, timeRemain)
        except KeyboardInterrupt:
            if Fake_interrupt:
                robots2Moves = [[0,0,0] for i in range(ROBOT_AMOUNT)]
                Fake_interrupt = False
            else:
                exit()
        '''
        
        VerifyOut(robots1Moves)
        VerifyOut(robots2Moves)

        ApplyMoves(robots1, robots1Moves)
        ApplyMoves(robots2, robots2Moves)
        
        SwitchBeacons(beacons, robots1, robots2)
        
        ApplyScore(beacons, scores)
        
        gamehistory.append(copy.deepcopy([robots1, robots2, beacons, scores, timeRemain]))
        timeRemain[0] -= 1
    return gamehistory

pygame.init()

screen = pygame.display.set_mode([SIZE_X,SIZE_Y])

#def DrawGame(gamehistory):
    

def addVecs(x,y):
    return (x[0]+y[0],x[1]+y[1])

def convertToDecart(coords):
    global HEX_SIZE
    x, y = SIZE_X/2, SIZE_Y/2
    x += coords[1] * HEX_SIZE * (1.5)
    y -= coords[0] * HEX_SIZE * (2 * sq3) + coords[1] * HEX_SIZE * sq3
    return (x, y)

def DrawHex(scr, coords):
    global HEX_COORDS
    pygame.draw.polygon(scr, BLACK, tuple(map(lambda x: addVecs(x, coords), HEX_COORDS)), 2)

def calcDistance(c1, c2):
    return (abs(c1[0] - c2[0]) + abs(c1[1] - c2[1]) + abs(c1[2] - c2[2]))//2

def DrawField(scr):
    for x in range(-MAP_SIZE, MAP_SIZE + 1):
        for y in range(-MAP_SIZE, MAP_SIZE + 1):
            z = - x - y
            if calcDistance((x,y,z), (0,0,0)) > MAP_SIZE:
                continue
            i, j = convertToDecart((x,y,z))
            DrawHex(scr, (i,j))
    
    
def DrawRobot(scr, pos, ID, team):
    global TEAM_COLORS
    koef = 1
    if team == 2:
        koef = -1
    pygame.draw.circle(scr, TEAM_COLORS[team], addVecs(convertToDecart(pos),\
                                                      (cos(PI/2 + koef * (PI / (ROBOT_AMOUNT + 1)) * (ID + 1)) * HEX_SIZE * 0.6,\
                                                       -sin(PI/2 + koef * (PI / (ROBOT_AMOUNT + 1)) * (ID + 1)) * HEX_SIZE * 0.6)), 4)

def DrawBeacon(scr, pos, team):
    global TEAM_COLORS
    pygame.draw.circle(scr, TEAM_COLORS[team], convertToDecart(pos), 7)

ft = pygame.font.Font(None, 20)

def DrawHelpInfo(scr, scores, timeRemain):
    score1pre = ft.render("Team 1: ", 0, BLACK, WHITE)
    score2pre = ft.render("Team 2: ", 0, BLACK, WHITE)
    timepre   = ft.render("Time remaining: ", 0, BLACK, WHITE)
    score1val = ft.render(str(scores[0]), 0, TEAM_COLORS[1], WHITE)
    score2val = ft.render(str(scores[1]), 0, TEAM_COLORS[2], WHITE)
    timeval   = ft.render(str(timeRemain[0]), 0, BLACK, WHITE)
    step0 = ft.size("Time remaining: ")
    step1 = ft.size("Team 1: ")
    x_value = SIZE_X // 8
    for ren in [timepre, timeval, score1pre, score1val, score2pre, score2val]:
        scr.blit(ren, (x_value, 10))
        if x_value == SIZE_X // 8:
            x_value += step0[0]
        elif x_value == SIZE_X // 8 + step0[0]:
            x_value = SIZE_X * 0.75
        else:
            x_value += step1[0]

def DrawFrame(scr, data):
    scr.fill(WHITE)
    DrawField(scr)
    r1, r2, bs, scores, tr = data
    for i in range(ROBOT_AMOUNT):
        DrawRobot(scr, r1[i], i, 1)
        DrawRobot(scr, r2[i], i, 2)
    for i in range(BEACON_AMOUNT):
        DrawBeacon(scr, bs[0][i], bs[1][i])
    DrawHelpInfo(scr, scores, tr)

try:
    exec("import {} as team1".format(sys.argv[1]))
    team1.Main = exit_after(0.125)(team1.Main)
except (ImportError, IndexError):
    print("Cannot import 1!")
    exit()

try:
    exec("import {} as team2".format(sys.argv[2]))
    team2.Main = exit_after(0.125)(team2.Main)
except (ImportError, IndexError):
    print("Cannot import 2!")
    exit()

gameHistory = PlayGame(team1.Main, team2.Main)
print(gameHistory[-1][3])
running = True
time = 0
while running:
    for i in pygame.event.get():
        if i.type == pygame.QUIT:
            running = False
    #print(time)
    DrawFrame(screen, gameHistory[time])
    time += 1
    if time == len(gameHistory):
        time = 0
    pygame.display.update()
    sleep(1/5)

exit()