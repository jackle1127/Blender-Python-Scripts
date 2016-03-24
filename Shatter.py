import bpy
import math
import random

NUM_OF_CUTS = 16
def transform(pt, object, reversed):
    point = []
    point.append(pt[0])
    point.append(pt[1])
    point.append(pt[2])
    if reversed == False:
        point[0] = point[0] * object.scale[0]
        point[1] = point[1] * object.scale[1]
        point[2] = point[2] * object.scale[2]
        
        #X rotation
        radius = math.sqrt(point[1] * point[1] + point[2] * point[2])
        original = math.atan2(point[2], point[1])
        point[1] = radius * math.cos(original + object.rotation_euler[0])
        point[2] = radius * math.sin(original + object.rotation_euler[0])
        #Y rotation
        radius = math.sqrt(point[0] * point[0] + point[2] * point[2])
        original = math.atan2(point[2], -point[0])
        point[0] = -radius * math.cos(original + object.rotation_euler[1])
        point[2] = radius * math.sin(original + object.rotation_euler[1])
        #Z rotation
        radius = math.sqrt(point[0] * point[0] + point[1] * point[1])
        original = math.atan2(point[1], point[0])
        point[0] = radius * math.cos(original + object.rotation_euler[2])
        point[1] = radius * math.sin(original + object.rotation_euler[2])
        
        point[0] = point[0] + object.location[0]
        point[1] = point[1] + object.location[1]
        point[2] = point[2] + object.location[2]
    else:
        point[0] = point[0] - object.location[0]
        point[1] = point[1] - object.location[1]
        point[2] = point[2] - object.location[2]
        
        #Z rotation
        radius = math.sqrt(point[0] * point[0] + point[1] * point[1])
        original = math.atan2(point[1], point[0])
        point[0] = radius * math.cos(original - object.rotation_euler[2])
        point[1] = radius * math.sin(original - object.rotation_euler[2])
        #Y rotation
        radius = math.sqrt(point[0] * point[0] + point[2] * point[2])
        original = math.atan2(point[2], -point[0])
        point[0] = -radius * math.cos(original - object.rotation_euler[1])
        point[2] = radius * math.sin(original - object.rotation_euler[1])
        #X rotation
        radius = math.sqrt(point[1] * point[1] + point[2] * point[2])
        original = math.atan2(point[2], point[1])
        point[1] = radius * math.cos(original - object.rotation_euler[0])
        point[2] = radius * math.sin(original - object.rotation_euler[0])
        
        point[0] = point[0] / object.scale[0]
        point[1] = point[1] / object.scale[1]
        point[2] = point[2] / object.scale[2]
    
    return (point[0], point[1], point[2])
    
def dotProduct(vector1, vector2):
    return vector1[0] * vector2[0] +\
    vector1[1] * vector2[1] +\
    vector1[2] * vector2[2]

def crossProduct(vector1, vector2):
    return (vector1[1] * vector2[2] - vector1[2] * vector2[1],
    vector1[2] * vector2[0] - vector1[0] * vector2[2],
    vector1[0] * vector2[1] - vector1[1] * vector2[0])

def toVector(point1, point2):
    return (point2[0] - point1[0],
    point2[1] - point1[1],
    point2[2] - point1[2])

def intersect(edge, planeVertices, planeNormal):
    deltaVector = toVector(edge[0], planeVertices[0])
    edgeVector = toVector(edge[0], edge[1])
    t = -1
    hybridDot = dotProduct(planeNormal, edgeVector)
    if hybridDot != 0:
        t = dotProduct(planeNormal, deltaVector) / hybridDot
    if t >= 0 and t <= 1:
        newVertex = (edge[0][0] + edgeVector[0] * t, edge[0][1] + edgeVector[1] * t, edge[0][2] + edgeVector[2] * t)
        abovePlane = edge[2]
        belowPlane = edge[3]
        if hybridDot >= 0:
            abovePlane = edge[3]
            belowPlane = edge[2]
        return (newVertex, abovePlane, belowPlane)
    else:
        return None

def createPolygon(mesh, vertexList):
    mesh.polygons.add(1)
    for vertex in vertexList:
        mesh.loops.add(1)
        mesh.loops[-1].vertex_index = vertex
    mesh.polygons[-1].loop_start = mesh.loops[-len(vertexList)].index
    mesh.polygons[-1].loop_total = len(vertexList)

def otherVertex(edge, vertex):
    if vertex == edge.vertices[0]: return edge.vertices[1]
    if vertex == edge.vertices[1]: return edge.vertices[0]
    return None

def normalFromMesh(mesh, vertexList):
    vector1 = toVector(mesh.vertices[vertexList[0]].co,
        mesh.vertices[vertexList[1]].co)
    vector2 = toVector(mesh.vertices[vertexList[0]].co,
        mesh.vertices[vertexList[2]].co)
    return crossProduct(vector1, vector2)

def normalFromObject(object, vertexList):
    mesh = object.data
    vector1 = toVector(transform(mesh.vertices[vertexList[0]].co, object, False),
        transform(mesh.vertices[vertexList[1]].co, object, False))
    vector2 = toVector(transform(mesh.vertices[vertexList[0]].co, object, False),
        transform(mesh.vertices[vertexList[2]].co, object, False))
    return crossProduct(vector1, vector2)
for object in bpy.context.selected_objects:
    for i in range(NUM_OF_CUTS):
        edgeCacheDict = {}
        objectEdgeDict = {}
        vertexEdgeDict = {}
        for edge in object.data.edges:
            objectEdgeDict.update({(edge.vertices[0], edge.vertices[1]):edge})
            objectEdgeDict.update({(edge.vertices[1], edge.vertices[0]):edge})
            if edge.vertices[0] not in vertexEdgeDict:
                vertexEdgeDict.update({edge.vertices[0]:[edge]})
            else:
                vertexEdgeDict[edge.vertices[0]].append(edge)

            if edge.vertices[1] not in vertexEdgeDict:
                vertexEdgeDict.update({edge.vertices[1]:[edge]})
            else:
                vertexEdgeDict[edge.vertices[1]].append(edge)

        sliceTopEdges = []
        sliceBottomEdges = []
        noShowPolygons = set()
        noShowEdges = {}
        newVertexId = 0
        newVerticesMap = {}
        newPlaneVertices = []
        anchorVertex = []
        for i in range(3):
            anchorVertex.append(object.location[i] + object.dimensions[i] * (random.random() - .5))
        for j in range(len(anchorVertex)):
            vertex = []
            for i in range(3):
                vertex.append(anchorVertex[i] + random.random() - .5)
            newPlaneVertices.append(tuple(vertex))
        planeNormal = crossProduct(toVector(newPlaneVertices[0], newPlaneVertices[1]),
                toVector(newPlaneVertices[0], newPlaneVertices[2]))

        newPolygons = []
        for polygon in object.data.polygons:
            addToNewPolygons = False
            newVertices = []
            for edgeKey in polygon.edge_keys:
                if edgeKey not in edgeCacheDict:
                    edge = (transform(object.data.vertices[edgeKey[0]].co, object, False), transform(object.data.vertices[edgeKey[1]].co, object, False), edgeKey[0], edgeKey[1])
                    newVertex = intersect(edge, newPlaneVertices, planeNormal)
                    if newVertex != None:
                        newVerticesMap.update({newVertexId: (transform(newVertex[0], object, True), newVertex[1])})
                        newVerticesMap.update({newVertexId + 1: (transform(newVertex[0], object, True), newVertex[2])})
                        edgeCacheDict.update({edgeKey:newVertexId})
                        newVertices.append(newVertexId)
                        newVertices.append(newVertexId + 1)
                        noShowEdges.update({newVertexId:objectEdgeDict[edgeKey]})
                        noShowEdges.update({newVertexId + 1:objectEdgeDict[edgeKey]})
                        noShowPolygons.add(polygon)
                        addToNewPolygons = True
                        newVertexId = newVertexId + 2
                    else:
                        edgeCacheDict.update({edgeKey:None})
                else:
                    if edgeCacheDict[edgeKey] is not None:
                        newVertices.append(edgeCacheDict[edgeKey])
                        newVertices.append(edgeCacheDict[edgeKey] + 1)
                        noShowPolygons.add(polygon)
                        addToNewPolygons = True

            if addToNewPolygons:
                vector1 = toVector(object.data.vertices[object.data.loops[polygon.loop_indices[0]].vertex_index].co,
                    object.data.vertices[object.data.loops[polygon.loop_indices[1]].vertex_index].co)
                vector2 = toVector(object.data.vertices[object.data.loops[polygon.loop_indices[1]].vertex_index].co,
                    object.data.vertices[object.data.loops[polygon.loop_indices[2]].vertex_index].co)
                normal = crossProduct(vector1, vector2)
                
                topVertices = []
                pointer = newVerticesMap[newVertices[0]][1]
                topVertices.append(pointer)
                edgeSet = set()
                edgeSet.add(noShowEdges[newVertices[0]])
                while pointer != newVerticesMap[newVertices[2]][1]:
                    for edge in vertexEdgeDict[pointer]:
                        otherVert = otherVertex(edge, pointer)
                        if otherVert in polygon.vertices and edge not in edgeSet:
                            pointer = otherVert
                            topVertices.append(pointer)
                            edgeSet.add(edge)
                            break
                newPolygons.append((newVertices[0], topVertices, newVertices[2], normal))
                
                bottomVertices = []
                pointer = newVerticesMap[newVertices[1]][1]
                bottomVertices.append(pointer)
                edgeSet = set()
                edgeSet.add(noShowEdges[newVertices[1]])
                while pointer != newVerticesMap[newVertices[3]][1]:
                    for edge in vertexEdgeDict[pointer]:
                        otherVert = otherVertex(edge, pointer)
                        if otherVert in polygon.vertices and edge not in edgeSet:
                            pointer = otherVert
                            bottomVertices.append(pointer)
                            edgeSet.add(edge)
                            break
                newPolygons.append((newVertices[1], bottomVertices, newVertices[3], normal))
                sliceTopEdges.append((newVertices[0], newVertices[2]))
                sliceBottomEdges.append((newVertices[1], newVertices[3]))

        name = object.data.name
        newMesh = bpy.data.meshes.new(name)
        for vertex in object.data.vertices:
            newMesh.vertices.add(1)
            newMesh.vertices[-1].co = vertex.co

        for polygon in object.data.polygons:
            if polygon not in noShowPolygons:
                newPolygonVertices = []
                for i in polygon.loop_indices:
                    newPolygonVertices.append(object.data.loops[i].vertex_index)
                createPolygon(newMesh, newPolygonVertices)

        newVertexCache = {}
        for newPolygon in newPolygons:
            newVertex1 = None
            newVertex2 = None
            if newPolygon[0] not in newVertexCache:
                newMesh.vertices.add(1)
                newMesh.vertices[-1].co = newVerticesMap[newPolygon[0]][0]
                newVertex1 = newMesh.vertices[-1].index
                newVertexCache.update({newPolygon[0]:newVertex1})
            else:
                newVertex1 = newVertexCache[newPolygon[0]]

            if newPolygon[2] not in newVertexCache:
                newMesh.vertices.add(1)
                newMesh.vertices[-1].co = newVerticesMap[newPolygon[2]][0]
                newVertex2 = newMesh.vertices[-1].index
                newVertexCache.update({newPolygon[2]:newVertex2})
            else:
                newVertex2 = newVertexCache[newPolygon[2]]

            newPolygonVertices = [newVertex1] + newPolygon[1] + [newVertex2]
            vector1 = toVector(newMesh.vertices[newVertex1].co,
                newMesh.vertices[newPolygon[1][0]].co)
            vector2 = toVector(newMesh.vertices[newPolygon[1][0]].co,
                newMesh.vertices[newVertex2].co)
            normal = crossProduct(vector1, vector2)
            if dotProduct(normal, newPolygon[3]) < 0:
                newPolygonVertices.reverse()
            createPolygon(newMesh, newPolygonVertices)

        object.data = newMesh
        bpy.data.meshes.remove(bpy.data.meshes[name])
        newMesh.name = name
        abort = False
        verticesToCover = set()
        for edge in sliceTopEdges:
            verticesToCover.add(edge[0])
            verticesToCover.add(edge[1])

        while len(verticesToCover) > 0:
            slicePolygon = []
            pointer = list(verticesToCover)[0]
            startingPosition = pointer
            slicePolygon.append(newVertexCache[pointer])
            edgeCache = set()
            verticesToCover.remove(pointer)
            while True:
                for edge in sliceTopEdges:
                    if pointer in edge and edge not in edgeCache:
                        edgeCache.add(edge)
                        if pointer == edge[0]:
                            pointer = edge[1]
                        else:
                            pointer = edge[0]
                        break
                if pointer == startingPosition:
                    break
                if pointer not in verticesToCover:
                    abort = True
                    break
                slicePolygon.append(newVertexCache[pointer])
                verticesToCover.remove(pointer)
            if not abort:
                normal = normalFromObject(object, slicePolygon[0:3])
                if dotProduct(normal, planeNormal) > 0:
                    slicePolygon.reverse()
                createPolygon(newMesh, slicePolygon)


        verticesToCover = set()
        for edge in sliceBottomEdges:
            verticesToCover.add(edge[0])
            verticesToCover.add(edge[1])

        while len(verticesToCover) > 0:
            slicePolygon = []
            pointer = list(verticesToCover)[0]
            startingPosition = pointer
            slicePolygon.append(newVertexCache[pointer])
            edgeCache = set()
            verticesToCover.remove(pointer)
            while True:
                for edge in sliceBottomEdges:
                    if pointer in edge and edge not in edgeCache:
                        edgeCache.add(edge)
                        if pointer == edge[0]:
                            pointer = edge[1]
                        else:
                            pointer = edge[0]
                        break
                if pointer == startingPosition:
                    break
                if pointer not in verticesToCover:
                    abort = True
                    break
                slicePolygon.append(newVertexCache[pointer])
                verticesToCover.remove(pointer)
            if not abort:
                normal = normalFromObject(object, slicePolygon[0:3])
                if dotProduct(normal, planeNormal) < 0:
                    slicePolygon.reverse()
                createPolygon(newMesh, slicePolygon)
        object.data.update(calc_edges=True, calc_tessface=True)
