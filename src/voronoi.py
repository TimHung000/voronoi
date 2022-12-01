from copy import deepcopy
from math import sqrt

def crossProduct(origin: 'Point', point1: 'Point', point2: 'Point'):
    line1X = point1.x - origin.x
    line1Y = point1.y - origin.y
    line2X = point2.x - origin.x
    line2Y = point2.y - origin.y

    return line1X * line2Y - line1Y * line2X

def getMidPoint(point1: 'Point', point2: 'Point') -> 'Point':
    return Point((point1.x+point2.x) / 2, (point1.y+point2.y)/2)

def distance(point1:'Point', point2:'Point'):
    return sqrt((point2.y - point1.y) ** 2 + (point2.x - point1.x) ** 2)

def getPerpendicularLine(line: 'Line', point: 'Point') -> 'Line':
    return Line(-line.yCoefficient, line.xCoefficient, -line.yCoefficient * point.x + line.xCoefficient * point.y)

def createLineByPoint(point1: 'Point', point2: 'Point') -> 'Line':
    """
    ax_1 + by_1 = c
    ax_2 + by_2 = c
    =>
    a(x_1 - x_2) + b(y_1 - y_2) = 0
    => 
    a = y_2 - y_1
    b = x_1 - x_2
    c = a * x_1 + b * y_1
    """
    xCoefficient = point2.y - point1.y
    yCoefficient = point1.x - point2.x
    constant = xCoefficient * point1.x + yCoefficient * point1.y
    return Line(xCoefficient, yCoefficient, constant)

def getXbyY(line: 'Line', y: float):
    return (line.constant - line.yCoefficient * y) / line.xCoefficient

def getYbyX(line: 'Line', x: float):
    return (line.constant - line.xCoefficient * x) / line.yCoefficient

def isIntersect(line1: 'Line', line2: 'Line') -> bool:
    return line1.xCoefficient * line2.yCoefficient != line2.xCoefficient * line1.yCoefficient

def findIntersection(line1: 'Line', line2: 'Line') -> 'Point':
    """
    use cramer's rule

    a_1x + b_1y = c_1
    a_2x + b_2y = c_2
    
    calculate the determinant of following 
    D    = |a_1 b_1| = a_1*b_2 - a_2*b_1
            |a_2 b_2|
    
    D_x  = |c_1 b_1| = c_1*b_2 - c_2*b_1
            |c_2 b_2|
    
    D_y  = |a_1 c_1| = a_1*c_2 - a_2*c_1
            |a_2 c_2|
    
    x = D_x / D
    y = D_y / D
    """
    if(isIntersect(line1, line2) == False):
        return None
    D = line1.xCoefficient * line2.yCoefficient - line2.xCoefficient * line1.yCoefficient
    Dx = line1.constant * line2.yCoefficient - line2.constant * line1.yCoefficient
    Dy = line1.xCoefficient * line2.constant - line2.xCoefficient * line1.constant
    x = Dx / D
    y = Dy / D
    return Point(x, y)

def isInDistrict(width, height, x, y):
    return x >= 0 and x <= width and y >= 0 and y <= height

def getIntersectionOfCanvas(width: int, height: int, line: 'Line') -> list['Point']:
    res = []

    if(line.xCoefficient == 0 or line.yCoefficient == 0):
        # perpendicular line
        if(line.xCoefficient == 0 and line.yCoefficient !=0 ):
            leftBound = Point(0, getYbyX(line, 0))
            rightBound = Point(width, getYbyX(line, width))
            res.append(leftBound)
            res.append(rightBound)
        # horizontal line
        elif(line.yCoefficient == 0 and line.xCoefficient != 0):
            lowerBound = Point(getXbyY(line, height), height)
            upperBound = Point(getXbyY(line, 0), 0)
            res.append(upperBound)
            res.append(lowerBound)
    else:
        lowerBound = Point(getXbyY(line, height), height)
        upperBound = Point(getXbyY(line, 0), 0)
        leftBound = Point(0 ,getYbyX(line, 0))
        rightBound = Point(width ,getYbyX(line, width))
        
        if(isInDistrict(width, height, lowerBound.x, lowerBound.y)):
            res.append(lowerBound)
        if(isInDistrict(width, height, leftBound.x, leftBound.y)):
            res.append(leftBound)
        if(isInDistrict(width, height, upperBound.x, upperBound.y)):
            res.append(upperBound)
        if(isInDistrict(width, height, rightBound.x, rightBound.y)):
            res.append(rightBound)

    return res

def mergeConvexHull(leftConvexHull: list['Point'], rightConvexHull: list['Point']):
    # leftConvexHull start point(right most)
    leftConvexHullRightestPointIdx = 0
    for i in range(1,len(leftConvexHull)):
        if(leftConvexHull[i].x > leftConvexHull[leftConvexHullRightestPointIdx].x or leftConvexHull[i].x == leftConvexHull[leftConvexHullRightestPointIdx].x and leftConvexHull[i].y > leftConvexHull[leftConvexHullRightestPointIdx].y):
            leftConvexHullRightestPointIdx = i
    

    # rightConvexHull start point(left most)
    rightConvexHullLeftestPointIdx = 0
    for i in range(1, len(rightConvexHull)):
        if(rightConvexHull[i].x < rightConvexHull[rightConvexHullLeftestPointIdx].x or rightConvexHull[i].x == rightConvexHull[rightConvexHullLeftestPointIdx].x and rightConvexHull[i].y < rightConvexHull[rightConvexHullLeftestPointIdx].y):
            rightConvexHullLeftestPointIdx = i 

    # find the upper tangent
    upperTangentLeft = leftConvexHullRightestPointIdx
    upperTangentRight = rightConvexHullLeftestPointIdx
    while(True):
        prevUpperTangentLeft = upperTangentLeft
        prevUpperTangentRight = upperTangentRight

        # find the uppertangent point in the right convexHull by moving right point clockwise
        # y-axis become smaller when we go up, so we use smaller instead of bigger than
        while(crossProduct(leftConvexHull[upperTangentLeft], rightConvexHull[upperTangentRight], rightConvexHull[(upperTangentRight+len(rightConvexHull)-1) % len(rightConvexHull)]) < 0):
            upperTangentRight = (upperTangentRight+len(rightConvexHull)-1) % len(rightConvexHull)
        
        # moving left convexhull point up
        while(crossProduct(rightConvexHull[upperTangentRight], leftConvexHull[upperTangentLeft], leftConvexHull[(upperTangentLeft+1) % len(leftConvexHull)]) > 0):
            upperTangentLeft = (upperTangentLeft+1) % len(leftConvexHull)
        
        if(upperTangentLeft == prevUpperTangentLeft and upperTangentRight == prevUpperTangentRight):
            break
    
    # find the lower tangent
    lowerTangentLeft = leftConvexHullRightestPointIdx
    lowerTangentRight = rightConvexHullLeftestPointIdx
    while(True):
        prevLowerTangentLeft = lowerTangentLeft
        prevLowerTangentRight = lowerTangentRight

        while(crossProduct(leftConvexHull[lowerTangentLeft], rightConvexHull[lowerTangentRight], rightConvexHull[(lowerTangentRight+1) % len(rightConvexHull)]) > 0):
            lowerTangentRight = (lowerTangentRight+1) % len(rightConvexHull)
        
        while(crossProduct(rightConvexHull[lowerTangentRight], leftConvexHull[lowerTangentLeft], leftConvexHull[(lowerTangentLeft+len(leftConvexHull)-1) % len(leftConvexHull)]) < 0):
            lowerTangentLeft = (lowerTangentLeft+len(leftConvexHull)-1) % len(leftConvexHull)
        
        if(lowerTangentLeft == prevLowerTangentLeft and lowerTangentRight == prevLowerTangentRight):
            break
    
    convexHull = []
    upperTangent = lowerTangent = None

    # in the same line
    if(rightConvexHull[upperTangentRight] == rightConvexHull[lowerTangentRight] and leftConvexHull[upperTangentLeft] == leftConvexHull[lowerTangentLeft]):

        upperTangent = Edge(rightConvexHull[upperTangentRight], leftConvexHull[upperTangentLeft])
        lowerTangent = Edge(leftConvexHull[lowerTangentLeft], rightConvexHull[lowerTangentRight])
        convexHull.extend(leftConvexHull)
        convexHull.extend(rightConvexHull)
    else:
        upperTangent = Edge(rightConvexHull[upperTangentRight], leftConvexHull[upperTangentLeft])
        lowerTangent = Edge(leftConvexHull[lowerTangentLeft], rightConvexHull[lowerTangentRight])

        index = upperTangentLeft
        while(True):
            convexHull.append(leftConvexHull[index])
            if(index == lowerTangentLeft):
                break
            index = (index + 1) % len(leftConvexHull)
        
        index = lowerTangentRight
        while(True):
            convexHull.append(rightConvexHull[index])
            if(index == upperTangentRight):
                break
            index = (index + 1) % len(rightConvexHull)  

    return convexHull, upperTangent, lowerTangent

def testCaseParser(file):
    testCases = []
    with open(file,'r') as file:
        remainingPoint = 0
        points = []
        for line in file:
            if line[0] == '#' or line.strip() == '':
                continue

            words = line.strip().split()
            if(len(words) == 1 and words[0] == '0' and remainingPoint == 0):
                break
            elif(len(words) == 1 and words[0] != '0' and remainingPoint == 0):
                remainingPoint = int(words[0])
            elif(len(words) == 2 and remainingPoint > 0):
                points.append((int(words[0]), int(words[1])))
                remainingPoint = remainingPoint - 1
            else:
                testCases.clear()
                break

            if(remainingPoint == 0):
                if(len(points) > 0):
                    testCases.append(points)
                    points = []
    return testCases

def voronoiFileParser(file):
    points = []
    edges = []
    with open(file, 'r') as file:
        for line in file:
            words = line.strip().split()
            if(words[0] == 'P'):
                points.append(Point(float(words[1]), float(words[2])))
            if(words[0] == 'E'):
                edges.append(Edge((Point(float(words[1]), float(words[2]))),Point(float(words[3]), float(words[4]))))
    return points, edges

def createVoronoiFile(file, points: list['Point'], edges: list['Edge']):
    writeFile = open(file, 'w')
    for point in points:
        writeFile.write(f"P {point.x} {point.y}\n")
    
    for edge in edges:
        writeFile.write(f"E {round(edge.start.x)} {round(edge.start.y)} {round(edge.end.x)} {round(edge.end.y)}\n")

    writeFile.close()

class Point():
    """
    point in 2d graph
    """
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.edges = []
    
    def __add__(self, rhs):
        return Point(self.x + rhs.x, self.y + rhs.y)

    def __sub__(self, rhs):
        return Point(self.x - rhs.x, self.y - rhs.y)
    def __repr__(self):
        return repr(f"({self.x}, {self.y})")


class Edge():
    """
    Doubly connected edge list
    """
    start: Point
    end: Point
    startInfinity: bool
    endInfinity: bool
    nextEdge: 'Edge'
    prevEdge: 'Edge'
    twinEdge: 'Edge'
    line: 'Line'
    face: 'Face'

    def __init__(self, start:Point = None, end:Point = None, startInfinity:bool = False, endInfinity:bool=False, outOfBound:bool = False, nextEdge=None, prevEdge=None, twinEdge=None, line=None, leftFace = None, rightFace = None, face = None):
        self.start = start
        self.end = end
        self.startInfinity = startInfinity
        self.endInfinity = endInfinity
        self.nextEdge = nextEdge
        self.prevEdge = prevEdge
        self.twinEdge = twinEdge
        self.line = line
        self.leftFace = leftFace
        self.rightFace = rightFace
        self.face = face
    
    def __repr__(self):
        return repr(f"start:({self.start.x}, {self.start.y}) end:({self.end.x}, {self.end.y}) face:({self.face.point.x}, {self.face.point.y})")


class Line():
    """
    ax+by=c
    """
    def __init__(self, xCoefficient=None, yCoefficient=None, constant=None):
        self.xCoefficient = xCoefficient
        self.yCoefficient = yCoefficient
        self.constant = constant


class Face():
    point: Point
    edges: list[Edge]
    def __init__(self, point:Point):
        self.point = point
        self.edges = []


class VoronoiRecord():
    edges: list[Edge]
    points: list[Point]
    convexHull: list[Edge]

    def __init__(self, voronoiGraph: 'VoronoiGraph'):
        self.edges = []
        self.points = []
        self.convexHull = []
        # the data structure use directed edge to form a polygon(counterclockwise)
        # In order to print out the line without duplicate, we filter out the duplicate line
        edge_set = set()
        for face in voronoiGraph.faces:
            self.points.append(face.point)
            for edge in face.edges:
                if edge in edge_set or edge.twinEdge in edge_set:
                    continue
                if(edge.start.x < edge.end.x or (edge.start.x == edge.end.x and edge.start.y <= edge.end.y)):
                    edge_set.add(edge)
                else:
                    edge_set.add(edge.twinEdge)
        edge_list = []
        for edge in edge_set:
            edge_list.append(Edge(Point(edge.start.x, edge.start.y), Point(edge.end.x, edge.end.y)))
        # edge_list = deepcopy(list(edge_set))
        edge_list.sort(key= lambda edge: (edge.start.x, edge.start.y, edge.end.x, edge.end.y))
        self.edges = edge_list
        if(len(voronoiGraph.convexHull) > 1):
            for i in range(len(voronoiGraph.convexHull)):
                self.convexHull.append(Edge(voronoiGraph.convexHull[i], voronoiGraph.convexHull[(i+1) % len(voronoiGraph.convexHull)]))


class MergeRecord():
    leftVoronoiRecord: VoronoiRecord
    rightVoronoiRecord: VoronoiRecord
    hyperPlane: list[Edge]
    newVornoiRecord: VoronoiRecord
    tangent: list[Edge]

    def __init__(self, leftVoronoiRecord: VoronoiRecord, rightVoronoiRecord: VoronoiRecord, hyperPlane: list[Edge], newVoronoiRecord: VoronoiRecord, tangent: list[Edge]):
        self.hyperPlane = []
        for edge in hyperPlane:
            self.hyperPlane.append(Edge(Point(edge.start.x, edge.start.y), Point(edge.end.x, edge.end.y)))

        self.leftVoronoiRecord = leftVoronoiRecord
        self.rightVoronoiRecord = rightVoronoiRecord
        self.newVornoiRecord = newVoronoiRecord
        self.tangent = tangent


class VoronoiGraph():
    canvasWidth: int
    canvasHeight: int
    faces: list[Face]
    edges: list[Edge]
    voronoiPoints: list[Point]
    convexHull: list[Point]
    mergeRecords: list[MergeRecord]

    def __init__(self, canvasWidth, canvasHeight):
        self.faces = []
        self.convexHull = []
        self.edges = []
        self.voronoiPoints = []
        self.mergeRecords = []
        self.canvasWidth = canvasWidth
        self.canvasHeight = canvasHeight
    
    def createVoronoiGraph(self, points:Point):
        if(len(points) == 1):
            self.convexHull.append(points[0])
            face = Face(points[0])
            self.faces.append(face)
            
        elif(len(points) == 2):
            # create face by point, left face is the leftest and uppurest
            leftFace = None
            rightFace = None
            points.sort(key= lambda point: (point.x, point.y))
            leftFace = Face(points[0])
            rightFace = Face(points[1])               

            # calulate the perpendicular line of left face and right face
            leftRightLine = createLineByPoint(leftFace.point, rightFace.point)
            midPoint = getMidPoint(leftFace.point, rightFace.point)
            perpendicularLine = getPerpendicularLine(leftRightLine, midPoint)

            # create hyperplane edge and sort by the y axis(if y axis of both point are the same, rightmost point are the first)
            intersectionsOfCanvas = getIntersectionOfCanvas(self.canvasWidth, self.canvasHeight, perpendicularLine)
            intersectionsOfCanvas.sort(key= lambda point: (point.y, -point.x))

            currentEdgeDown = Edge(start=intersectionsOfCanvas[0], end=intersectionsOfCanvas[len(intersectionsOfCanvas)-1], startInfinity=True, endInfinity=True, line=perpendicularLine, face=rightFace)
            currentEdgeUp = Edge(start=intersectionsOfCanvas[len(intersectionsOfCanvas)-1], end=intersectionsOfCanvas[0], startInfinity=True, endInfinity=True, line=perpendicularLine, face=leftFace)
            intersectionsOfCanvas[0].edges.append(currentEdgeDown)
            intersectionsOfCanvas[len(intersectionsOfCanvas)-1].edges.append(currentEdgeUp)
            currentEdgeDown.twinEdge = currentEdgeUp
            currentEdgeUp.twinEdge = currentEdgeDown
            currentEdgeDown.face = rightFace
            currentEdgeUp.face = leftFace
            leftFace.edges.append(currentEdgeUp)
            rightFace.edges.append(currentEdgeDown)
            self.faces.append(leftFace)
            self.faces.append(rightFace)
            self.convexHull.append(leftFace.point)
            self.convexHull.append(rightFace.point)
        else:
            leftVoronoiGraph = VoronoiGraph(self.canvasWidth, self.canvasHeight)
            leftVoronoiGraph.createVoronoiGraph(points[:len(points) // 2])
            rightVoronoiGraph = VoronoiGraph(self.canvasWidth, self.canvasHeight)
            rightVoronoiGraph.createVoronoiGraph(points[len(points) // 2:])
            self.mergeVoronoiDiagram(leftVoronoiGraph, rightVoronoiGraph)

    def mergeVoronoiDiagram(self, leftVoronoiGraph: 'VoronoiGraph', rightVoronoiGraph: 'VoronoiGraph'):
        # left and right voronoi Record are used by the step by step execution
        leftVoronoiRecord = VoronoiRecord(leftVoronoiGraph)
        rightVoronoiRecord = VoronoiRecord(rightVoronoiGraph)

        # find the left and right face as the start scan line
        convexHull, upperTangent, lowerTangent = mergeConvexHull(leftVoronoiGraph.convexHull, rightVoronoiGraph.convexHull)
        leftFace: Face = None
        rightFace: Face = None
        for face in leftVoronoiGraph.faces:
            if(face.point == upperTangent.end):
                leftFace = face
                break
        for face in rightVoronoiGraph.faces:
            if(face.point == upperTangent.start):
                rightFace = face
                break

        hyperPlaneDown: list[Edge] = []
        hyperPlaneUp: list[Edge] = []
        prevIntersection: Point = None
        prevIntersectedEdgeList: list[Edge] = []
        modifiedEdgeList: list[list[Edge]] = []
        modifiedEdgeBelongList: list[list[int]] = []
        while(True):
            # reach the lower tangent
            if(leftFace.point == lowerTangent.start and rightFace.point == lowerTangent.end):
                break

            # calulate the perpendicular line of two faces as hyperplane
            leftRightLine = createLineByPoint(leftFace.point, rightFace.point)
            midPoint = getMidPoint(leftFace.point, rightFace.point)
            perpendicularLine = getPerpendicularLine(leftRightLine, midPoint)

            # find the intersection of perpendicular line and canvas edge(use as default start and end point of edge)
            currentHyperPlaneIntersectionsOfCanvas = getIntersectionOfCanvas(self.canvasWidth, self.canvasHeight, perpendicularLine)
            currentHyperPlaneIntersectionsOfCanvas.sort(key= lambda point: (point.y, -point.x))
            startPoint = currentHyperPlaneIntersectionsOfCanvas[0]
            startPointInfinity = True
            endPoint = currentHyperPlaneIntersectionsOfCanvas[len(currentHyperPlaneIntersectionsOfCanvas)-1]
            endPointInfinity = True

            # find the nearest intersection and nearest edge which is the end point of hyperline
            nearestEdgeList: list[Edge] = []
            nearestEdgeBelongList: list[int] = [] # 0: leftVoronoi, 1: rightVoronoi
            nearestIntersection: Point = None

            for leftEdge in leftFace.edges:
                if leftEdge.twinEdge in prevIntersectedEdgeList:
                    continue

                intersection = findIntersection(perpendicularLine, leftEdge.line)
                if(prevIntersection != None and intersection != None and (intersection.y < prevIntersection.y or (intersection.x == prevIntersection.x and intersection.y == prevIntersection.y))):
                    continue

                if(intersection != None and (nearestIntersection == None or intersection.y < nearestIntersection.y or (intersection.y == nearestIntersection.y and intersection.x > nearestIntersection.x))):
                    nearestEdgeList.clear()
                    nearestEdgeBelongList.clear()
                    nearestEdgeList.append(leftEdge)
                    nearestEdgeBelongList.append(0)
                    nearestIntersection = intersection 
                elif(intersection != None and nearestIntersection != None and (intersection.y == nearestIntersection.y and intersection.x == nearestIntersection.x)):
                    nearestEdgeList.append(leftEdge)
                    nearestEdgeBelongList.append(0)

            for rightEdge in rightFace.edges:
                if rightEdge.twinEdge in prevIntersectedEdgeList:
                    continue

                intersection = findIntersection(perpendicularLine, rightEdge.line)
                if(prevIntersection != None and intersection != None and (intersection.y < prevIntersection.y or (intersection.x == prevIntersection.x and intersection.y == prevIntersection.y))):
                    continue

                if(intersection != None and (nearestIntersection == None or intersection.y < nearestIntersection.y or (intersection.y == nearestIntersection.y and intersection.x < nearestIntersection.x))):
                    nearestEdgeList.clear()
                    nearestEdgeBelongList.clear()
                    nearestEdgeList.append(rightEdge)
                    nearestEdgeBelongList.append(1)
                    nearestIntersection = intersection
                elif(intersection != None and nearestIntersection != None and (intersection.y == nearestIntersection.y and intersection.x == nearestIntersection.x)):
                    nearestEdgeList.append(rightEdge)
                    nearestEdgeBelongList.append(1)
            
            # nearest intersection are the same as previous
            if(prevIntersection != None and nearestIntersection.x == prevIntersection.x and nearestIntersection.y == prevIntersection.y):
                for i in range(len(nearestEdgeList)):
                    if(nearestEdgeBelongList[i] == 0):
                        leftFace = nearestEdgeList[i].twinEdge.face
                    if(nearestEdgeBelongList[i] == 1):
                        rightFace = nearestEdgeList[i].twinEdge.face
                continue

            # assign connected edge to the voronoi point, if intersection already exist just use that point as intersection
            leftIntersectCount = len([elem for elem in nearestEdgeBelongList if elem == 0])
            rightIntersectCount = len([elem for elem in nearestEdgeBelongList if elem == 1])

            if(leftIntersectCount > 1):
                edgeIdx = nearestEdgeBelongList.index(0)
                if(nearestEdgeList[edgeIdx].start.x == nearestIntersection.x and nearestEdgeList[edgeIdx].start.y == nearestIntersection.y):
                    nearestIntersection = nearestEdgeList[edgeIdx].start
                elif(nearestEdgeList[edgeIdx].end.x == nearestIntersection.x and nearestEdgeList[edgeIdx].end.y == nearestIntersection.y):
                    nearestIntersection = nearestEdgeList[edgeIdx].end

            if(rightIntersectCount > 1):
                edgeIdx = nearestEdgeBelongList.index(1)
                if(nearestEdgeList[edgeIdx].start.x == nearestIntersection.x and nearestEdgeList[edgeIdx].start.y == nearestIntersection.y):
                    nearestIntersection = nearestEdgeList[edgeIdx].start
                elif(nearestEdgeList[edgeIdx].end.x == nearestIntersection.x and nearestEdgeList[edgeIdx].end.y == nearestIntersection.y):
                    nearestIntersection = nearestEdgeList[edgeIdx].end

            for i in range(len(nearestEdgeList)):
                if(nearestEdgeBelongList[i] == 0 and leftIntersectCount == 1):
                    nearestIntersection.edges.append(nearestEdgeList[i].twinEdge)
                elif(nearestEdgeBelongList[i] == 1 and rightIntersectCount == 1):
                    nearestIntersection.edges.append(nearestEdgeList[i])

            # seting the start point of current hyperplane
            if(len(hyperPlaneDown) > 0):
                startPoint = hyperPlaneDown[len(hyperPlaneDown)-1].end
                startPointInfinity = False
            elif(len(hyperPlaneDown) == 0):
                if(not isInDistrict(self.canvasWidth,self.canvasHeight, nearestIntersection.x, nearestIntersection.y)):
                    # the start point of hyperPlane is infinity, so we find a point outside the canvas and is farther than intersection
                    if(nearestIntersection.x < 0 and startPoint.x < endPoint.x or nearestIntersection.x > self.canvasWidth and startPoint.x > endPoint.x):
                        if(perpendicularLine.xCoefficient == 0):
                            startPoint.x = nearestIntersection.x - (endPoint.x - startPoint.x)
                        else:
                            startPoint.x = nearestIntersection.x - (endPoint.x - startPoint.x)
                            startPoint.y = getYbyX(perpendicularLine, nearestIntersection.x - (endPoint.x - startPoint.x))
                    elif(nearestIntersection.y < 0 and startPoint.y < endPoint.y or nearestIntersection.y > self.canvasHeight and startPoint.y > endPoint.y):
                        if(perpendicularLine.yCoefficient == 0):
                            startPoint.y = nearestIntersection.y - (endPoint.y - startPoint.y)
                        else:
                            startPoint.x = getXbyY(perpendicularLine, nearestIntersection.y - (endPoint.y - startPoint.y))
                            startPoint.y = nearestIntersection.y - (endPoint.y - startPoint.y)

            prevIntersectedEdgeList = nearestEdgeList
            prevIntersection = nearestIntersection
            endPoint = nearestIntersection
            endPointInfinity = False

            # create hyperplane edge
            currentEdgeDown = Edge(start=startPoint, end=endPoint, startInfinity=startPointInfinity, endInfinity=endPointInfinity, line=perpendicularLine, face=rightFace)
            currentEdgeUp = Edge(start=endPoint, end=startPoint, startInfinity=endPointInfinity, endInfinity=startPointInfinity, line=perpendicularLine, face=leftFace)
            currentEdgeDown.twinEdge = currentEdgeUp
            currentEdgeUp.twinEdge = currentEdgeDown
            startPoint.edges.append(currentEdgeDown)
            endPoint.edges.append(currentEdgeUp)
            hyperPlaneDown.append(currentEdgeDown)
            hyperPlaneUp.append(currentEdgeUp)
            modifiedEdgeList.append(nearestEdgeList)
            modifiedEdgeBelongList.append(nearestEdgeBelongList)

            # finding the next face
            if(leftIntersectCount > 1):
                leftNearestEdge = nearestEdgeList[0:leftIntersectCount]
                leftNearestEdge.sort(key= lambda edge: (-edge.twinEdge.face.point.y, -edge.twinEdge.face.point.x))
                leftFace = leftNearestEdge[0].twinEdge.face

            if(rightIntersectCount > 1):
                rightNearestEdge = nearestEdgeList[leftIntersectCount:leftIntersectCount+rightIntersectCount]
                rightNearestEdge.sort(key= lambda edge: (-edge.twinEdge.face.point.y, edge.twinEdge.face.point.x))
                rightFace = rightNearestEdge[0].twinEdge.face
            
            for i in range(len(nearestEdgeList)):
                if(nearestEdgeBelongList[i] == 0 and leftIntersectCount == 1):
                    leftFace = nearestEdgeList[i].twinEdge.face
                if(nearestEdgeBelongList[i] == 1 and rightIntersectCount == 1):
                    rightFace = nearestEdgeList[i].twinEdge.face

        ###################################################### Handle last hyperline #######################################################################
        # calulate the perpendicular line of lower tangent as last hyperplane
        leftRightLine = createLineByPoint(leftFace.point, rightFace.point)
        midPoint = getMidPoint(leftFace.point, rightFace.point)
        perpendicularLine = getPerpendicularLine(leftRightLine, midPoint)

        currentHyperPlaneIntersectionsOfCanvas = getIntersectionOfCanvas(self.canvasWidth, self.canvasHeight, perpendicularLine)
        currentHyperPlaneIntersectionsOfCanvas.sort(key= lambda point: (point.y, -point.x))
        startPoint = currentHyperPlaneIntersectionsOfCanvas[0]
        startPointInfinity = True
        endPoint = currentHyperPlaneIntersectionsOfCanvas[len(currentHyperPlaneIntersectionsOfCanvas)-1]
        endPointInfinity = True

        # intersection not in the canvas
        if(len(hyperPlaneDown) > 0):
            if(not isInDistrict(self.canvasWidth,self.canvasHeight, hyperPlaneDown[len(hyperPlaneDown)-1].end.x, hyperPlaneDown[len(hyperPlaneDown)-1].end.y)):
                if(hyperPlaneDown[len(hyperPlaneDown)-1].end.x > self.canvasWidth and endPoint.x > startPoint.x or hyperPlaneDown[len(hyperPlaneDown)-1].end.x < 0 and endPoint.x < startPoint.x):
                    if(perpendicularLine.xCoefficient == 0):
                        endPoint.x = hyperPlaneDown[len(hyperPlaneDown)-1].end.x + (endPoint.x - startPoint.x)
                    else:
                        endPoint.x = hyperPlaneDown[len(hyperPlaneDown)-1].end.x + (endPoint.x - startPoint.x)
                        endPoint.y = getYbyX(perpendicularLine, hyperPlaneDown[len(hyperPlaneDown)-1].end.x + (endPoint.x - startPoint.x))
                elif(hyperPlaneDown[len(hyperPlaneDown)-1].end.y > self.canvasHeight and endPoint.y > startPoint.y or hyperPlaneDown[len(hyperPlaneDown)-1].end.y < 0 and endPoint.y < startPoint.y):
                    if(perpendicularLine.yCoefficient == 0):
                        endPoint.y = hyperPlaneDown[len(hyperPlaneDown)-1].end.y + (endPoint.y - startPoint.y)
                    else:
                        endPoint.x = getYbyX(perpendicularLine, hyperPlaneDown[len(hyperPlaneDown)-1].end.y + (endPoint.y - startPoint.y))
                        endPoint.y = hyperPlaneDown[len(hyperPlaneDown)-1].end.y + (endPoint.y - startPoint.y)

            startPoint = hyperPlaneDown[len(hyperPlaneDown)-1].end
            startPointInfinity = False

        # create hyperplane edge
        currentEdgeDown = Edge(start=startPoint, end=endPoint, startInfinity=startPointInfinity, endInfinity=endPointInfinity, line=perpendicularLine, face=rightFace)
        currentEdgeUp = Edge(start=endPoint, end=startPoint, startInfinity=endPointInfinity, endInfinity=startPointInfinity, line=perpendicularLine, face=leftFace)
        startPoint.edges.append(currentEdgeDown)
        endPoint.edges.append(currentEdgeUp)
        currentEdgeDown.twinEdge = currentEdgeUp
        currentEdgeUp.twinEdge = currentEdgeDown
        hyperPlaneDown.append(currentEdgeDown)
        hyperPlaneUp.append(currentEdgeUp)

        # Intersected Point outside of canvas. If other side of edge is infinity move the other side of point far than the intersected point
        for i in range(len(modifiedEdgeList)):
            for j in range(len(modifiedEdgeList[i])):
                # left voronoi graph
                if(modifiedEdgeBelongList[i][j] == 0):
                    if(modifiedEdgeList[i][j].startInfinity == True and not isInDistrict(self.canvasWidth, self.canvasHeight, hyperPlaneDown[i].end.x, hyperPlaneDown[i].end.y)):
                        if(hyperPlaneDown[i].end.x > self.canvasWidth and modifiedEdgeList[i][j].start.x > modifiedEdgeList[i][j].end.x or hyperPlaneDown[i].end.x < 0 and modifiedEdgeList[i][j].start.x < modifiedEdgeList[i][j].end.x):
                            xCoordinate = hyperPlaneDown[i].end.x - (modifiedEdgeList[i][j].end.x - modifiedEdgeList[i][j].start.x)
                            yCoordinate = getYbyX(modifiedEdgeList[i][j].line, xCoordinate)
                            self.changeEdgePoint(modifiedEdgeList[i][j], 'start', xCoordinate, yCoordinate)

                        elif(hyperPlaneDown[i].end.y > self.canvasHeight and modifiedEdgeList[i][j].start.y > modifiedEdgeList[i][j].end.y or hyperPlaneDown[i].end.y < 0 and modifiedEdgeList[i][j].start.y < modifiedEdgeList[i][j].end.y):
                            yCoordinate = hyperPlaneDown[i].end.y - (modifiedEdgeList[i][j].end.y - modifiedEdgeList[i][j].start.y)
                            xCoordinate = getXbyY(modifiedEdgeList[i][j].line, yCoordinate)
                            self.changeEdgePoint(modifiedEdgeList[i][j], 'start', xCoordinate, yCoordinate)
                # right voronoi graph
                elif(modifiedEdgeBelongList[i][j] == 1):                    
                    if(modifiedEdgeList[i][j].endInfinity == True and not isInDistrict(self.canvasWidth, self.canvasHeight, hyperPlaneDown[i].end.x, hyperPlaneDown[i].end.y)):
                        if(hyperPlaneDown[i].end.x > self.canvasWidth and modifiedEdgeList[i][j].end.x > modifiedEdgeList[i][j].start.x or hyperPlaneDown[i].end.x < 0 and modifiedEdgeList[i][j].end.x < modifiedEdgeList[i][j].start.x):
                            xCoordinate = hyperPlaneDown[i].end.x + (modifiedEdgeList[i][j].end.x - modifiedEdgeList[i][j].start.x)
                            yCoordinate = getYbyX(modifiedEdgeList[i][j].line, xCoordinate)
                            self.changeEdgePoint(modifiedEdgeList[i][j], 'end', xCoordinate, yCoordinate)

                        elif(hyperPlaneDown[i].end.y > self.canvasHeight and modifiedEdgeList[i][j].end.y > modifiedEdgeList[i][j].start.y or hyperPlaneDown[i].end.y < 0 and modifiedEdgeList[i][j].end.y < modifiedEdgeList[i][j].start.y):
                            yCoordinate = hyperPlaneDown[i].end.y + (modifiedEdgeList[i][j].end.y - modifiedEdgeList[i][j].start.y)
                            xCoordinate = getXbyY(modifiedEdgeList[i][j].line, yCoordinate)
                            self.changeEdgePoint(modifiedEdgeList[i][j], 'end', xCoordinate, yCoordinate)


        # trim the extended line and delete the unconnected line
        for i in range(len(modifiedEdgeList)):
            for j in range(len(modifiedEdgeList[i])):
                # left voronoi graph
                if(modifiedEdgeBelongList[i][j] == 0):
                    # based on the trimming of extended line, removed the line that connect to the trim out line
                    for edge in modifiedEdgeList[i][j].face.edges:
                        if(edge != modifiedEdgeList[i][j] and edge.start == modifiedEdgeList[i][j].end and crossProduct(hyperPlaneDown[i].end, hyperPlaneDown[i+1].end, edge.end) < 0):
                            self.removeEdge(edge)
                    for edge in modifiedEdgeList[i][j].twinEdge.face.edges:
                        if(edge != modifiedEdgeList[i][j].twinEdge and edge.end == modifiedEdgeList[i][j].twinEdge.start and crossProduct(hyperPlaneDown[i].end, hyperPlaneDown[i+1].end, edge.start) < 0):
                            self.removeEdge(edge)
                    # trim out the extended line based on the intersected point
                    if(modifiedEdgeList[i][j].start == hyperPlaneDown[i].end):
                        self.removeEdge(modifiedEdgeList[i][j])
                    else:
                        modifiedEdgeList[i][j].end = hyperPlaneDown[i].end
                        modifiedEdgeList[i][j].endInfinity = False
                        modifiedEdgeList[i][j].twinEdge.start = hyperPlaneDown[i].end
                        modifiedEdgeList[i][j].twinEdge.startInfinity = False

                # right voronoi graph
                elif(modifiedEdgeBelongList[i][j] == 1):
                    # based on the trimming of extended line, removed the line that connect to the trim out line
                    for edge in modifiedEdgeList[i][j].face.edges:
                        if(edge != modifiedEdgeList[i][j] and edge.end == modifiedEdgeList[i][j].start and crossProduct(hyperPlaneDown[i].end, hyperPlaneDown[i+1].end, edge.start) > 0):
                            self.removeEdge(edge)
                    for edge in modifiedEdgeList[i][j].twinEdge.face.edges:
                        if(edge != modifiedEdgeList[i][j].twinEdge and edge.start == modifiedEdgeList[i][j].twinEdge.end and crossProduct(hyperPlaneDown[i].end, hyperPlaneDown[i+1].end, edge.end) > 0):
                            self.removeEdge(edge)
                    # trim out the extended line based on the intersected point
                    if(modifiedEdgeList[i][j].end == hyperPlaneDown[i].end):
                        self.removeEdge(modifiedEdgeList[i][j])
                    else:
                        modifiedEdgeList[i][j].start = hyperPlaneDown[i].end
                        modifiedEdgeList[i][j].startInfinity = False
                        modifiedEdgeList[i][j].twinEdge.end = hyperPlaneDown[i].end
                        modifiedEdgeList[i][j].twinEdge.endInfinity = False
            
        # delete the unconnected line
        for face in leftVoronoiGraph.faces:
            for edge in face.edges:
                if((edge.startInfinity == False and len(edge.start.edges) == 1) or (edge.endInfinity == False and len(edge.end.edges) == 1)):
                    self.removeEdge(edge)

        for face in rightVoronoiGraph.faces:
            for edge in face.edges:
                if((edge.startInfinity == False and len(edge.start.edges) == 1) or (edge.endInfinity == False and len(edge.end.edges) == 1)):
                    self.removeEdge(edge)

        hyperPlaneUp.reverse()
        for edge in hyperPlaneUp:
            edge.face.edges.append(edge)
        for edge in hyperPlaneDown:
            edge.face.edges.insert(0, edge)

        self.convexHull = convexHull
        self.faces.extend(leftVoronoiGraph.faces)
        self.faces.extend(rightVoronoiGraph.faces)

        newVoronoiRecord = VoronoiRecord(self)
        tangent = [upperTangent, lowerTangent]
        mergeRecord = MergeRecord(leftVoronoiRecord, rightVoronoiRecord, hyperPlaneDown, newVoronoiRecord, tangent)
        self.mergeRecords.extend(leftVoronoiGraph.mergeRecords)
        self.mergeRecords.extend(rightVoronoiGraph.mergeRecords)
        self.mergeRecords.append(mergeRecord)

    def removeEdge(self, edge: Edge):
        twinEdge = edge.twinEdge
        if(edge in edge.face.edges):
            edge.face.edges.remove(edge)
        if(twinEdge in twinEdge.face.edges):
            twinEdge.face.edges.remove(twinEdge)
        if(edge in edge.start.edges):
            edge.start.edges.remove(edge)
        if(twinEdge in twinEdge.start.edges):
            twinEdge.start.edges.remove(twinEdge)

    def changeEdgePoint(self, edge:Edge, start_end, x, y):
        """
        :param edge: the point's edge
        :param start_end: 0: start, 1: end 
        :param x: new point x coord
        :param y: new point y coord
        """
        if(start_end == 'start'):
            edge.start.x = x
            edge.start.y = y
            edge.twinEdge.end.x = x
            edge.twinEdge.end.y = y
        elif(start_end == 'end'):
            edge.end.x = x
            edge.end.y = y
            edge.twinEdge.start.x = x
            edge.twinEdge.start.y = y


class Voronoi():
    canvasWidth: int
    canvasHeight: int
    voronoiGraph: VoronoiGraph
    points: list[Point]
    edges: list[Edge]
    currentStep: int

    def __init__(self, canvasWidth, canvasHeight):
        self.canvasWidth = canvasWidth
        self.canvasHeight = canvasHeight
        self.voronoiGraph = None
        self.points = []
        self.edges = []
        self.currentStep = 0
    
    def buildVoronoiDiagram(self, points):
        # sort the points fisrt by x and then by y
        points.sort(key=lambda point: (point.x, point.y))
        remove_duplicate = []
        remove_duplicate.append(points[0])
        for i in range(1,len(points)):
            if(points[i].x == points[i-1].x and points[i].y == points[i-1].y):
                continue
            remove_duplicate.append(points[i])
        self.points = remove_duplicate

        # build the voronoi diagram base on the points given
        self.voronoiGraph = VoronoiGraph(self.canvasWidth, self.canvasHeight)
        self.voronoiGraph.createVoronoiGraph(self.points)

        # the data structure use directed edge to form a polygon(counterclockwise)
        # In order to print out the line without duplicate, we filter out the duplicate line
        edge_set = set()
        for face in self.voronoiGraph.faces:
            for edge in face.edges:
                if edge in edge_set or edge.twinEdge in edge_set:
                    continue
                if(edge.start.x < edge.end.x or edge.start.x == edge.end.x and edge.start.y <= edge.end.y):
                    edge_set.add(edge)
                else:
                    edge_set.add(edge.twinEdge)
                    
        edge_list = list(edge_set)
        edge_list.sort(key= lambda edge: (edge.start.x, edge.start.y, edge.end.x, edge.end.y))
        self.edges = edge_list
    
    def clear(self):
        self.points = []
        self.edges = []
        self.currentStep = 0
        self.voronoiGraph = None
    
