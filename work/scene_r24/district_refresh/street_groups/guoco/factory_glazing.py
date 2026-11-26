"""Build the factory's independently inset glazing, painted timber and opening casement."""
import bpy


def glaze_material(name, rgb, roughness, metal=0.):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    material.diffuse_color = (*rgb, 1.)
    node = material.node_tree.nodes.get('Principled BSDF')
    node.inputs['Base Color'].default_value = (*rgb, 1.)
    node.inputs['Metallic'].default_value = metal
    node.inputs['Roughness'].default_value = roughness
    return material


class Glazing:
    def __init__(self):
        self.finish = [glaze_material(f'Factory recessed pane {i + 1}', rgb, rough, .43)
                       for i, (rgb, rough) in enumerate([
                           ((.105,.177,.201),.30), ((.052,.121,.139),.28), ((.024,.071,.079),.37),
                           ((.077,.151,.153),.32), ((.038,.091,.082),.38), ((.153,.217,.230),.33)])]
        self.wood = glaze_material('Factory worn dark umber timber ribs', (.09,.048,.032), .68)
        self.units = 0
        self.opened = 0

    def __call__(self, mesh, point, low, high, sill, head, side, bay, storey):
        self.units += 1
        # Two frames flank the historic central bar. Small height changes catch
        # different light at each reveal while the glass stays behind the brick face.
        w = high - low
        h = head - sill
        columns = [low + w * i / 6 for i in range(7)]
        bands = [sill, sill + h * .37, sill + h * .69, head]
        for column, (a, b) in enumerate(zip(columns, columns[1:])):
            for row, (bottom, top) in enumerate(zip(bands, bands[1:])):
                finish = self.finish[(2*bay + 3*side + 3*row + column + storey) % len(self.finish)]
                back = .275 + .004 * ((side + bay + column) % 3)
                mesh.face([point(a+.014,back,bottom+.015),point(b-.014,back,bottom+.015),
                           point(b-.014,back,top-.014),point(a+.014,back,top-.014)], finish)
        for u in columns[1:-1]:
            mesh.face([point(u-.013,.231,sill),point(u+.013,.231,sill),
                       point(u+.013,.231,head),point(u-.013,.231,head)], self.wood)
        if side == 0 and storey == 1 and bay == 3:
            self.opened += 1
            # The observed opening type is used on this low-front mock-up bay.
            a, b = columns[1], columns[3]
            z0, z1 = bands[0] + .08, bands[2] - .045
            panel = [point(a,.229,z0),point(b,-.15,z0),point(b,-.15,z1),point(a,.229,z1)]
            mesh.face(panel, self.finish[2])
            mesh.face(panel[::-1], self.finish[2])
            for z in (z0, (z0+z1)*.5, z1):
                mesh.face([point(a,.215,z-.017),point(b,-.17,z-.017),point(b,-.17,z+.017),point(a,.215,z+.017)],self.wood)
            for x, depth in ((a,.217),(b,-.169)):
                mesh.face([point(x-.02,depth,z0),point(x+.02,depth,z0),
                           point(x+.02,depth,z1),point(x-.02,depth,z1)],self.wood)
