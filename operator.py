import bpy
import os
import subprocess
import threading
import bmesh
from bmesh.types import BMVert
import mathutils
import math
from pathlib import Path

class DRMoldUnitOperator(bpy.types.Operator):
    bl_idname = "drmold.set_units"
    bl_label = "DRMold: Set Units To MM Scale"
    bl_description = "DRMold: Set the unit system so that 1 unit is 1 mm."

    def execute(self, context):
        bpy.context.scene.unit_settings.system="METRIC"
        bpy.context.scene.unit_settings.length_unit="MILLIMETERS"
        bpy.context.scene.unit_settings.scale_length=0.001

        return {'FINISHED'}

class DRMoldCleanupOperator(bpy.types.Operator):
    bl_idname = "drmold.cleanup"
    bl_label = "DRMold: Cleanup"
    bl_description = "DRMold: Cleanup"

    def execute(self, context):
        collection = DRMoldHelper.cleanUp(context, bpy.context.active_object)

        return {'FINISHED'}

class DRMoldOperator(bpy.types.Operator):
    bl_idname = "drmold.doall"
    bl_label = "DRMold: Do it all"
    bl_description = "DRMold: Do it all"

    collection = None

    def execute(self, context):
        self.shape = bpy.context.active_object

        DRMoldHelper.makeShellHalves(context, self.shape)
        DRMoldHelper.getBaseShape(context, self.shape)

        return {'FINISHED'}

class DRAddVClampOperator(bpy.types.Operator):
    bl_idname = "drmold.addvclamp"
    bl_label = "DRMold: Add vertical clamp"
    bl_description = "DRMold: Add vertical clamp"

    collection = None

    def execute(self, context):
        mesh = DRMoldHelper.getAddonPartMesh("ClampCutoutVertical", replace=False)
        cube = DRMoldHelper.makeCube(1,1,1)
        cube.name = "ClampCutoutVertical"
        cube.data = mesh
        DRMoldHelper.moveToCollection(cube, DRMoldHelper.getColCutouts())

        return {'FINISHED'}

class DRAddHClampOperator(bpy.types.Operator):
    bl_idname = "drmold.addhclamp"
    bl_label = "DRMold: Add horizontal clamp"
    bl_description = "DRMold: Add horizontal clamp"

    collection = None

    def execute(self, context):
        mesh = DRMoldHelper.getAddonPartMesh("ClampCutoutHorizontal", replace=False)
        cube = DRMoldHelper.makeCube(1,1,1)
        cube.name = "ClampCutoutHorizontal"
        cube.data = mesh
        DRMoldHelper.moveToCollection(cube, DRMoldHelper.getColCutouts())

        return {'FINISHED'}

class DRAddPinOperator(bpy.types.Operator):
    bl_idname = "drmold.addpin"
    bl_label = "DRMold: Add pin"
    bl_description = "DRMold: Add pin"

    collection = None

    def execute(self, context):
        mesh = DRMoldHelper.getAddonPartMesh("PinCutout", replace=False)
        cube = DRMoldHelper.makeCube(1,1,1)
        cube.name = "PinCutout"
        cube.data = mesh
        DRMoldHelper.moveToCollection(cube, DRMoldHelper.getColCutouts())

        return {'FINISHED'}

class DRAddFunnelOperator(bpy.types.Operator):
    bl_idname = "drmold.addfunnel"
    bl_label = "DRMold: Add funnel"
    bl_description = "DRMold: Add funnel"

    collection = None

    def execute(self, context):
        cone = DRMoldHelper.makeCone(60, 60)
        cone.rotation_euler = (math.radians(180), 0, 0)
        DRMoldHelper.moveToCollection(cone, DRMoldHelper.getColShellAdditions())
        v = DRMoldHelper.getHighestVertex(bpy.context.active_object)
        v[2] += 30-20
        cone.location = v

        cone = DRMoldHelper.makeCone(90, 120)
        cone.rotation_euler = (math.radians(180), 0, 0)
        DRMoldHelper.moveToCollection(cone, DRMoldHelper.getColGloveAdditions())
        v = DRMoldHelper.getHighestVertex(bpy.context.active_object)
        v[2] += 60-20
        cone.location = v

        return {'FINISHED'}
    


class DRMoldHelper():
    @classmethod
    def cleanUp(cls, context, obj):
        collection = cls.getColMoldTemp(delete_existing=True)

    @classmethod
    def getDraftAngledModel(cls, context, obj):
        parent = cls.getParentModel(obj)
        if not parent:
            return
        props = parent.dr_molds
        prop = props.mold_draft_angle
        if not prop:
            prop = cls.duplicateToTempCollection(obj, cls.getColMoldTemp())
            cls.extrudeSweep(prop, (-100, 0, 0)) # use half-width of object instead
            cls.remeshDefault(prop)
            cls.symmetrize(prop)
            prop.name = obj.name + "-1a-DraftAngle"
            prop.data.name = prop.name
            prop.hide_set(True)
            props.mold_draft_angle = prop
            prop.dr_molds.mold_parent = parent
        return prop

    @classmethod
    def getGloveSurface(cls, context, obj):
        parent = cls.getParentModel(obj)
        if not parent:
            return
        props = parent.dr_molds
        prop = props.mold_glove_surface
        if not prop:
            prop = cls.inflatedCopy(cls.getDraftAngledModel(context, obj), props.glove_thickness, cls.getColMoldTemp())
            prop.name = obj.name + "-1b-MoldSurface"
            prop.data.name = prop.name
            prop.hide_set(True)
            props.mold_glove_surface = prop
            prop.dr_molds.mold_parent = parent
        return prop

    @classmethod
    def getGloveInflated(cls, context, obj):
        parent = cls.getParentModel(obj)
        if not parent:
            return
        props = parent.dr_molds
        prop = props.mold_glove_inflated
        if not prop:
            prop = cls.inflatedCopy(cls.getGloveSurface(context, obj), props.glove_rim_height, cls.getColMoldTemp())
            prop.name = obj.name + "-1c-MoldInflated"
            prop.data.name = prop.name
            prop.hide_set(True)
            props.mold_glove_inflated = prop
            prop.dr_molds.mold_parent = parent
        return prop

    @classmethod
    def getGloveMoldComplete(cls, context, obj):
        parent = cls.getParentModel(obj)
        if not parent:
            return
        props = parent.dr_molds
        prop = props.mold_glove_complete
        if not prop:
            prop = cls.duplicateToTempCollection(cls.getGloveSurface(context, obj), cls.getColMoldTemp())
            inflatedRim = cls.getGloveInflated(context, obj)
            
            ribShape = cls.makeMoldRib(props.glove_rim_width)
            
            cls.intersectWith(ribShape, inflatedRim)
            cls.unionWith(prop, ribShape)
            cls.deleteObject(ribShape)
            cls.unionWithCollection(prop, cls.getColGloveAdditions())
            prop.name = obj.name + "-1d-GloveMold"
            prop.data.name = prop.name
            prop.hide_set(True)
            props.mold_glove_complete = prop
            prop.dr_molds.mold_parent = parent
        return prop
    
    @classmethod
    def getShellBase(cls, context, obj):
        parent = cls.getParentModel(obj)
        if not parent:
            return
        props = parent.dr_molds
        prop = props.mold_shell_base
        if not prop:
            prop = cls.inflatedCopy(cls.getGloveInflated(context, obj), props.shell_thickness, cls.getColMoldTemp())
            prop.name = obj.name + "-2a-MoldShellBase"
            prop.data.name = prop.name
            prop.hide_set(True)

            props.mold_shell_base = prop
            prop.dr_molds.mold_parent = parent
        return prop

    @classmethod
    def getShellOrganic(cls, context, obj):
        parent = cls.getParentModel(obj)
        if not parent:
            return
        props = parent.dr_molds
        prop = props.mold_shell_organic
        if not prop:
            prop = cls.duplicateToTempCollection(cls.getShellBase(context, obj), cls.getColMoldTemp())
            prop.name = obj.name + "-2b-MoldShellOrganic"
            prop.data.name = prop.name
            prop.hide_set(True)

            # overhang stuff
            overhangDir = (0, 0, -1)
            if(props.sides_upside_down):
                overhangDir = (0, 0, 1)
            cls.makePrintable(prop, dir=overhangDir, angle=45)
            cls.remeshDefault(prop)

            obj2 = cls.inflatedCopy(prop, props.shell_rim_height, cls.getCollection("MoldTemp", delete_existing=False))
            
            obj3 = cls.makeCube(1000, 1000, props.shell_rim_width)
            cls.intersectWith(obj3, obj2)

            baseAngle = 45
            if(not props.sides_upside_down):
                baseAngle = 90 - 22.5
            cls.makePrintable(obj3, dir=(0, 0, 1), angle=baseAngle)
            cls.remeshDefault(obj3)
            cls.unionWith(prop, obj3)
            cls.deleteObject(obj3)

            obj3 = cls.makeCube(props.shell_rim_width, 1000, 1000)
            cls.intersectWith(obj3, obj2)
            cls.unionWith(prop, obj3)
            cls.deleteObject(obj3)

            cls.deleteObject(obj2)

            cls.unionWithCollection(prop, cls.getColShellAdditions())

            props.mold_shell_organic = prop
            prop.dr_molds.mold_parent = parent
        return prop
    
    @classmethod
    def getClipPlane(cls, depth):
        prop = cls.makeCube(5000, 5000, 5000)
        prop.location = (0, 0, -2500 - depth)
        return prop
    
    @classmethod
    def getShellFinished(cls, context, obj):
        parent = cls.getParentModel(obj)
        if not parent:
            return
        props = parent.dr_molds
        prop = props.mold_shell_finished
        if not prop:
            prop = cls.duplicateToTempCollection(cls.getShellOrganic(context, obj), cls.getColMoldTemp())

            obj2 = cls.getClipPlane(0)
            cls.differenceWith(prop, obj2)
            cls.deleteObject(obj2)

            obj2 = cls.getGloveMoldComplete(context, obj)
            cls.differenceWith(prop, obj2)
            prop.name = obj.name + "-2c-MoldShellFinished"
            prop.data.name = prop.name
            prop.hide_set(True)
            props.mold_shell_finished = prop
            prop.dr_molds.mold_parent = parent
        return prop
    
    @classmethod
    def makeShellHalves(cls, context, obj):
        cls.getShellHalf(context, obj, True)
        cls.getShellHalf(context, obj, False)
    
    @classmethod
    def getShellHalf(cls, context, obj, leftHalf):
        parent = cls.getParentModel(obj)
        if not parent:
            return
        props = parent.dr_molds
        halfName = "MoldShellRight"
        if leftHalf:
            halfName = "MoldShellLeft"
        prop = cls.getPointerProperty(obj, halfName)
        if not prop:
            prop = DRMoldHelper.duplicateToTempCollection(cls.getShellFinished(context, obj), cls.getColMoldTemp())
            cube = cls.makeCube(5000, 5000, 5000)
            cube.location = (2500, 0, 2000)
            if leftHalf:
                cube.location = (-2500, 0, 2000)
            cls.intersectWith(prop, cube)
            cls.deleteObject(cube)
            prop.name = obj.name + "-2d-" + halfName
            prop.data.name = prop.name
            prop.hide_set(False)
            cls.setPointerProperty(obj, halfName, prop)
            num = 0
            if(leftHalf):
                num = 1
            #props.mold_shell_half[num] = prop
            prop.dr_molds.mold_parent = parent
        return prop

    @classmethod
    def getBaseShape(cls, context, obj):
        parent = cls.getParentModel(obj)
        if not parent:
            return
        props = parent.dr_molds
        prop = props.mold_base_shape
        if not prop:
            prop = cls.duplicateToTempCollection(cls.getShellOrganic(context, obj), cls.getColMoldTemp())

            cls.extrudeIntersection(prop, 15)
            
            cls.unionWith(prop, obj)

            obj2 = cls.getClipPlane(10)
            cls.differenceWith(prop, obj2)
            cls.deleteObject(obj2)

            prop.name = obj.name + "-3a-MoldBaseShape"
            prop.data.name = prop.name
            prop.hide_set(False)
            props.mold_base_shape = prop
            prop.dr_molds.mold_parent = parent
        return prop

    @classmethod
    def getColMoldTemp(cls, delete_existing=False):
        return cls.getCollection("MoldTemp", delete_existing=delete_existing)

    @classmethod
    def getColCutouts(cls, delete_existing=False):
        return cls.getCollection("MoldCutouts", delete_existing=delete_existing)

    @classmethod
    def getColGloveAdditions(cls, delete_existing=False):
        return cls.getCollection("GloveMoldAdditions", delete_existing=delete_existing)

    @classmethod
    def getColShellAdditions(cls, delete_existing=False):
        return cls.getCollection("ShellAdditions", delete_existing=delete_existing)

    @classmethod
    def getParentModel(cls, obj):
        i = 0
        if obj:
            while(obj.dr_molds.mold_parent and i < 10):
                obj = obj.dr_molds.mold_parent
                i += 1 # avoid infinite loops
        return obj

    @classmethod
    def extrudeIntersection(cls, obj, height):
        mesh = obj.data
        bm = bmesh.new()
        bm.from_mesh(mesh)
        
        geom_cut, geom = bmesh.ops.bisect_plane(bm, geom=bm.verts[:]+bm.edges[:]+bm.faces[:], dist=0.001, plane_co=(0,0,0), plane_no=(0,0,1), use_snap_center=True, clear_outer=True, clear_inner=True)
        bmesh.ops.edgeloop_fill(bm, edges=bm.edges, mat_nr=0, use_smooth=False)
        faces = bm.faces
        extruded = bmesh.ops.extrude_face_region(bm, geom=faces)
        
        translate_verts = [v for v in extruded['geom'] if isinstance(v, BMVert)]

        bmesh.ops.translate(bm, vec=(0, 0, -height), verts=translate_verts)

        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

        bm.to_mesh(mesh)
    
    @classmethod
    def makePrintable(cls, obj, dir = (0, 0, 1), angle = 45):
        mesh = obj.data
        bm = bmesh.new()
        bm.from_mesh(mesh)
        dir = mathutils.Vector(dir)
        dot = math.sin(math.radians(angle)) # higher angle = harsher overhangs
        dirNorm = dir.normalized()
        extrudeFaces = []
        for face in bm.faces:
            if(face.normal.dot(dirNorm) > dot):
                extrudeFaces.append(face)
        extruded = bmesh.ops.extrude_face_region(bm, geom=extrudeFaces)

        bm.verts.ensure_lookup_table()
        
        # Move extruded geometry
        translate_verts = [v for v in extruded['geom'] if isinstance(v, BMVert)]

        distMult = 1 / math.tan(math.radians(angle))

        for vert in translate_verts:
            modvec = mathutils.Vector(vert.co)
            vHeight = modvec.dot(dir)
            modvec -= dir * vHeight
            dist = modvec.length # distance to the side
            
            vec = mathutils.Vector(vert.co)

            vec = mathutils.Vector(dir) * (vHeight + dist * distMult)
            #vec[2] += dist
            #vec[0] = 0
            #vec[1] = 0
            vert.co = vec

        

        bmesh.ops.delete(bm, geom=extrudeFaces, context="FACES")

        bm.to_mesh(mesh)

    @classmethod
    def convexHull(cls, obj):
        mesh = obj.data
        bm = bmesh.new()
        bm.from_mesh(mesh)
        copy = obj.copy()
        ch = bpy.data.meshes.new("%s convexhull" % mesh.name)
        geom = bmesh.ops.convex_hull(bm, input=bm.verts)
        bm.to_mesh(ch)
        copy.name = "blah"
        copy.data = ch
        bpy.context.scene.collection.objects.link(copy)

    @classmethod
    def extrudeSweep(cls, obj, dir):
        mesh = obj.data
        bm = bmesh.new()
        bm.from_mesh(mesh)
        dir = mathutils.Vector(dir)
        dirNorm = dir.normalized()
        extrudeFaces = []
        for face in bm.faces:
            if(face.normal.dot(dirNorm) > 0):
                extrudeFaces.append(face)
        extruded = bmesh.ops.extrude_face_region(bm, geom=extrudeFaces)
        
        # Move extruded geometry
        translate_verts = [v for v in extruded['geom'] if isinstance(v, BMVert)]

        bmesh.ops.translate(bm, vec=dir, verts=translate_verts)

        

        bmesh.ops.delete(bm, geom=extrudeFaces, context="FACES")

        bm.to_mesh(mesh)
    
    @classmethod
    def symmetrize(cls, obj):
        mesh = obj.data
        bm = bmesh.new()
        bm.from_mesh(mesh)
        
        out = bmesh.ops.symmetrize(bm, input=bm.verts[:]+bm.edges[:]+bm.faces[:], direction="X")

        bm.to_mesh(mesh)

    @classmethod
    def getHighestVertex(cls, obj):
        mesh = obj.data
        bm = bmesh.new()
        bm.from_mesh(mesh)
        
        bm.verts.ensure_lookup_table()
        highestVert = None
        highestZ = 0
        for v in bm.verts:
            if v.co[2] > highestZ:
                highestZ = v.co[2]
                highestVert = v.co
        
        if(not highestVert):
            return None
        return mathutils.Vector(highestVert)

    @classmethod
    def selectObject(cls, obj):
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

    @classmethod
    def remesh(cls, obj, radius):
        mod = obj.modifiers.new("Remesh", "REMESH")
        mod.mode = "VOXEL"
        mod.voxel_size = radius
        
        cls.applyModifiers(obj)
    
    @classmethod
    def remeshDefault(cls, obj):
        parent = cls.getParentModel(obj)
        if not parent:
            return
        props = parent.dr_molds
        cls.remesh(obj, props.remesh_resolution)

    @classmethod
    def intersectWith(cls, obj, otherobj):
        cls.booleanWith(obj, otherobj, 0)
    
    @classmethod
    def unionWith(cls, obj, otherobj):
        cls.booleanWith(obj, otherobj, 1)
    
    @classmethod
    def differenceWith(cls, obj, otherobj):
        cls.booleanWith(obj, otherobj, 2)
    
    @classmethod
    def booleanWith(cls, obj, otherobj, mode):
        mod = obj.modifiers.new("Boolean", "BOOLEAN")
        mod.object = otherobj
        switcher = {
            0: "INTERSECT",
            1: "UNION",
            2: "DIFFERENCE"
        }
        mod.operation = switcher.get(mode, "UNION")
        cls.applyModifiers(obj)

    @classmethod
    def intersectWithCollection(cls, obj, collection):
        cls.booleanWithCollection(obj, collection, 0)
    
    @classmethod
    def unionWithCollection(cls, obj, collection):
        cls.booleanWithCollection(obj, collection, 1)
    
    @classmethod
    def differenceWithCollection(cls, obj, collection):
        cls.booleanWithCollection(obj, collection, 2)

    @classmethod
    def booleanWithCollection(cls, obj, collection, mode):
        mod = obj.modifiers.new("Boolean", "BOOLEAN")
        mod.collection = collection
        mod.operand_type = "COLLECTION"
        switcher = {
            0: "INTERSECT",
            1: "UNION",
            2: "DIFFERENCE"
        }
        mod.operation = switcher.get(mode, "UNION")
        cls.applyModifiers(obj)

    @classmethod
    def applyModifiers(cls, obj):
        sel = bpy.context.active_object
        cls.selectObject(obj)
        for mod in obj.modifiers:
            bpy.ops.object.modifier_apply(modifier = mod.name)
        
        cls.selectObject(sel)

    @classmethod
    def duplicateToTempCollection(cls, obj, col):
        obj2 = obj.copy()
        obj2.data = obj.data.copy()
        col.objects.link(obj2)
        cls.applyModifiers(obj2)
        return obj2

    @classmethod
    def moveToCollection(cls, obj, col):
        for c in obj.users_collection:
            c.objects.unlink(obj)
        col.objects.link(obj)

    @classmethod
    def deleteObject(cls, objectToDelete):
        bpy.data.objects.remove(objectToDelete, do_unlink=True)

    @classmethod
    def getCollection(cls, name, delete_existing=False):
        collection = bpy.context.scene.collection.children.get(name, None)
        if(collection == None):
            collection = bpy.data.collections.new(name)
            bpy.context.scene.collection.children.link(collection)
        else:
            if delete_existing:
                for child in collection.objects:
                    cls.deleteObject(child)
        return collection

    @classmethod
    def makeMoldRib(cls, thickness):
        obj = cls.makeCube(thickness, 5000, 5000)
        obj2 = cls.makeCube(5000, 5000, thickness)
        cls.unionWith(obj, obj2)
        cls.deleteObject(obj2)
        return obj

    @classmethod
    def makeCone(cls, radius, height):
        sel = bpy.context.active_object
        bpy.ops.mesh.primitive_cone_add(location=(0,0,0), radius1=radius, radius2=0, depth=height)
        cone = bpy.context.active_object
        cls.selectObject(sel)
        return cone
    
    @classmethod
    def makeCube(cls, x, y, z):
        sel = bpy.context.active_object
        bpy.ops.mesh.primitive_cube_add(location=(0,0,0), size=1, scale=(x*2, y*2, z*2))
        bpy.ops.object.transform_apply(location = False, scale = True, rotation = False)
        cube = bpy.context.active_object
        cls.selectObject(sel)
        return cube

    @classmethod
    def inflatedCopy(cls, object, radius, col):
        rmc = cls.duplicateToTempCollection(object, col)
        cls.inflateObject(rmc, radius)
        cls.remeshDefault(rmc)
        return rmc
    
    @classmethod
    def inflateObject(cls, obj, radius):
        cls.makeVertexGroup(obj)
        mod = obj.modifiers.new("Solidify", "SOLIDIFY")
        mod.offset = 1
        mod.thickness = radius
        mod.use_even_offset = True
        mod.use_quality_normals = True
        mod.shell_vertex_group = "toDelete"

        mod = obj.modifiers.new("Mask", "MASK")
        mod.invert_vertex_group = True
        mod.vertex_group = "toDelete"

        cls.applyModifiers(obj)
    
    @classmethod
    def makeVertexGroup(cls, obj):
        if(obj.vertex_groups.get("toDelete", None) == None):
            obj.vertex_groups.new( name = "toDelete" )
    
    def minkowskiInThread(self, inFile, outFile, radius):
        file = open("MinkowskiExpand.scad")

        line = file.read().format(stlfile=inFile, radius=radius)
        file.close()

        scadFile = self.getTempDir() + os.path.splitext(outFile)[0] + ".scad"
        print("scadfile: " + scadFile)

        file = open(scadFile, "w")
        file.write(line)
        file.close()

        out = self.getTempDir() + outFile
        ost = openSCADThread(self.openSCAD, scadFile, out)
        ost.start()
        return ost
    
    @classmethod
    def exportSTL(cls, obj, name):
        cls.selectObject(obj)
        
        bpy.ops.export_mesh.stl(filepath=cls.getTempDir() + name + ".stl", check_existing=False, use_selection=True)

        cls.selectObject(self.shape)

    @classmethod
    def setPointerProperty(cls, obj, prop, ref):
        obj[prop] = ref.name
    
    @classmethod
    def getPointerProperty(cls, obj, prop):
        name = cls.getPropOrNull(obj, prop)
        if not name:
            return None
        return bpy.data.objects.get(name, None)

    @classmethod
    def deletePointerPropertyAndObject(cls, obj, prop):
        o = cls.getPointerProperty(obj, prop)
        if o:
            cls.deleteObject(o)
        cls.deleteProperty(obj, prop)

    @classmethod
    def deleteProperty(cls, obj, prop):
        del obj[prop]
    
    @classmethod
    def getPropOrNull(cls, obj, prop):
        return obj.get(prop, None)

    @classmethod
    def getPrefs(cls, context):
        return context.preferences.addons["Mold_Addon"].preferences
    
    @classmethod
    def getTempDir(cls): # Deleted after the end of the session
        #return bpy.app.tempdir
        dir = bpy.path.abspath("//MoldTemp/")
        Path(dir).mkdir(exist_ok=True)
        return dir
        
    @classmethod
    def getAddonPartMesh(cls, name, replace):
        mesh = bpy.data.meshes.get(name, None)
        #if(mesh and replace):
            #bpy.data.meshes.remove(mesh, do_unlink=True)
            #mesh = None
        if(not mesh):
            filename = name
            directory = cls.getAddonPath() + "\MoldBits.blend\\Mesh\\"
            bpy.ops.wm.append(filename=filename, directory=directory, instance_object_data=False)
            mesh = bpy.data.meshes.get(name, None)
        return mesh

    @classmethod
    def getAddonPath(cls):
        script_file = os.path.realpath(__file__)
        return os.path.dirname(script_file)

    @classmethod
    def getOpenSCAD(cls, context):
        return cls.getPrefs(context).filepath

class openSCADThread(threading.Thread):
    def __init__(self, exe, inFile, outFile):
        self.stdout = None
        self.stderr = None
        self.exe = exe
        self.inFile = inFile
        self.outFile = outFile
        threading.Thread.__init__(self)
    
    def run(self):
        subprocess.call([self.exe, "-o", self.outFile, self.inFile])
    