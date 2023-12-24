ROBOT_AMOUNT = 5
BEACON_AMOUNT = 5
BEACON_LOCATIONS = ((0,6,-6), (6,-6, 0), (0,0,0), (6,0,-6), (-6,0,6))
TIME_MAX = 200
TEAM1_INIT_LOC = [0,-6,6]
TEAM2_INIT_LOC = [-6,6,0]

def calcDistance(c1, c2):
    return (abs(c1[0] - c2[0]) + abs(c1[1] - c2[1]) + abs(c1[2] - c2[2]))//2

def MoveFromTo(coords1, coords2):
    delta = [0,0,0]
    for i in range(3):
        delta[i] = coords2[i] - coords1[i]
    if delta == [0,0,0]:
        return delta
    result = [0,0,0]
    for i in range(3):
        if delta[i] > 0:
            result[i] = 1
            break
    for i in range(3):
        if delta[i] < 0:
            result[i] = -1
            break
    return result
    

def Main(team, robots1, robots2, beacons, scores, timeRemain):
    if team == 1:
        myrobots = robots1
    else:
        myrobots = robots2
    
    enemy_beacons = []
    for i in range(BEACON_AMOUNT):
        if beacons[1][i] != team:
            enemy_beacons.append(beacons[0][i])
    
    if len(enemy_beacons) != 0:
        result = [[0,0,0] for i in range(ROBOT_AMOUNT)]
        for i in range(ROBOT_AMOUNT):
            distances = list(map(lambda x : calcDistance(myrobots[i], x), enemy_beacons))
            minimum = min(distances)
            counter = 0
            index = -1
            while counter < i:
                index += 1
                if index == len(distances):
                    index = 0
                if distances[index] == minimum:
                    counter+=1
            result[i] = MoveFromTo(myrobots[i], enemy_beacons[index])
        return result
    else:
        result = [[0,0,0] for i in range(ROBOT_AMOUNT)]
        for i in range(ROBOT_AMOUNT):
            distances = list(map(lambda x : calcDistance(myrobots[i], x), beacons[0]))
            minimum = min(distances)
            counter = 0
            index = -1
            while counter < i:
                index += 1
                if index == len(distances):
                    index = 0
                if distances[index] == minimum:
                    counter+=1
            result[i] = MoveFromTo(myrobots[i], beacons[0][index])
        return result