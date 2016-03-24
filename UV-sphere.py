import bpy
import math

#Just create a UV sphere....
#Like the primitive UV sphere...
#Nothing special...
radius = 1
vertical = 60
horizontal = 60

sphereMesh = bpy.data.meshes.new("sphere mesh")
sphere = bpy.data.objects.new("sphere", sphereMesh)
sphereMesh.vertices.add(vertical * horizontal + 2)
bpy.context.scene.objects.link(sphere)
sphereMesh.vertices[0].co = (0, 0, radius)
sphereMesh.vertices[-1].co = (0, 0, -radius)

for i in range(1, len(sphereMesh.vertices) - 1):
    u = int((i - 1) % horizontal)
    v = int((i - 1) / horizontal)
    z = radius * math.cos(math.pi * (v + 1) / (vertical + 1))
    diskRadius = radius * math.sin(math.pi * (v + 1) / (vertical + 1))
    x = diskRadius * math.cos(2 * math.pi * u / horizontal)
    y = diskRadius * math.sin(2 * math.pi * u / horizontal)
    sphereMesh.vertices[i].co = (x, y, z)
    
for i in range(0, horizontal):
    sphereMesh.loops.add(3)
    sphereMesh.loops[-3].vertex_index = 0
    sphereMesh.loops[-2].vertex_index = i + 1
    sphereMesh.loops[-1].vertex_index = (i + 1) % horizontal + 1
    sphereMesh.polygons.add(1)
    sphereMesh.polygons[-1].loop_start = len(sphereMesh.loops) - 3
    sphereMesh.polygons[-1].loop_total = 3
    sphereMesh.loops.add(3)
    sphereMesh.loops[-3].vertex_index = len(sphereMesh.vertices) - 1 - horizontal + i
    sphereMesh.loops[-2].vertex_index = len(sphereMesh.vertices) - 1
    sphereMesh.loops[-1].vertex_index = len(sphereMesh.vertices) - 1 - horizontal + (i + 1) % horizontal
    sphereMesh.polygons.add(1)
    sphereMesh.polygons[-1].loop_start = len(sphereMesh.loops) - 3
    sphereMesh.polygons[-1].loop_total = 3

for i in range(0, vertical - 1):
    for j in range(0, horizontal):
        sphereMesh.loops.add(4)
        sphereMesh.loops[-4].vertex_index = 1 + horizontal * i + (j + 1) % horizontal
        sphereMesh.loops[-3].vertex_index = 1 + horizontal * i + j
        sphereMesh.loops[-2].vertex_index = 1 + horizontal * i + j + horizontal
        sphereMesh.loops[-1].vertex_index = 1 + horizontal * i + (j + 1) % horizontal + horizontal
        sphereMesh.polygons.add(1)
        sphereMesh.polygons[-1].loop_start = len(sphereMesh.loops) - 4
        sphereMesh.polygons[-1].loop_total = 4
sphereMesh.update()