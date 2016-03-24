import bpy
import math

#Create a sphere out of cubes.

radius = 6
cube = bpy.context.object.data
for z in range(-radius, radius):
    planeRadius = int(math.sqrt(radius * radius - z * z))
    for y in range(-planeRadius, planeRadius):
        lineRadius = int(math.sqrt(planeRadius * planeRadius - y * y))
        for x in range(-lineRadius, lineRadius):
            newCube = bpy.data.objects.new("Cube sphere", cube)
            newCube.location = (x * 2, y * 2, z * 2)
            bpy.context.scene.objects.link(newCube)
bpy.ops.object.select_pattern(pattern="Cube sphere*")
bpy.ops.rigidbody.objects_add()