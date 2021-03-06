import bpy, sys, os
import string
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty, IntProperty, FloatProperty, FloatVectorProperty, PointerProperty
from bpy.types import Operator, Header
import bmesh

# Update Blender UI Panels
# def tag_redraw(context, space_type="PROPERTIES", region_type="WINDOW"):
#     for window in context.window_manager.windows:
#         for area in window.screen.areas:
#             if area.spaces[0].type == space_type:
#                 for region in area.regions:
#                     if region.type == region_type:
#                         region.tag_redraw()


class TMG_UV_Properties(bpy.types.PropertyGroup):
    uvName : bpy.props.StringProperty(name='UVMap', default='UVMap', description='Name to set uv layer to')
    clear_seams : bpy.props.BoolProperty(name="Clear Seams", default=False, description='Remove UV seams')
    island_seams : bpy.props.BoolProperty(name="Island Seams", default=False, description='Add seams to islands after unwrap')

    mark_sharp : bpy.props.BoolProperty(name="Mark Sharp", default=False, description='Select and mark sharp edges')
    sharpness : bpy.props.FloatProperty(name="sharpness", default=0.87, min=0.01, soft_max=3.14, description='Edge sharpness for uv calculations')

    unwrapTypes : bpy.props.EnumProperty(name='Method', default='Smart_Project', description='',
    items=[
    ('Unwrap', 'Unwrap', ''),
    ('Smart_Project', 'Smart_Project', ''),
    ('Lightmap', 'Lightmap', '')
    ])

    packMethod : bpy.props.EnumProperty(name='Pack', default='individual', description='',
    items=[
    ('individual', 'individual', ''),
    ('all_together', 'all_together', '')
    ])

    selectAllFaces : bpy.props.BoolProperty(name="select all faces", default=False, description='Select all faces before unwrapping')

    # smart_project
    sp_angle_limit : bpy.props.FloatProperty(name="angle_limit", default=45.0, min=0, soft_max=99.0, description='')
    sp_area_weight : bpy.props.FloatProperty(name="area_weight", default=0.2, min=0, soft_max=1.0, description='')
    sp_correct_aspect : bpy.props.BoolProperty(name="correct_aspect", default=True, description='')
    sp_scale_to_bounds : bpy.props.BoolProperty(name="scale_to_bounds", default=False, description='')
    sp_margin : bpy.props.FloatProperty(name="margin", default=0.002, min=0, soft_max=1.0, description='')

    # Unwrap
    unwrapMethod : bpy.props.EnumProperty(name='Method', default='ANGLE_BASED', description='',
    items=[
    ('ANGLE_BASED', 'ANGLE_BASED', ''),
    ('CONFORMAL', 'CONFORMAL', '')
    ])

    un_fill_holes : bpy.props.BoolProperty(name="fill_holes", default=True, description='')
    un_correct_aspect : bpy.props.BoolProperty(name="correct_aspect", default=True, description='')
    un_use_subsurf_data : bpy.props.BoolProperty(name="use_subsurf_data", default=False, description='')
    un_margin : bpy.props.FloatProperty(name="margin", default=0.03, min=0, soft_max=1.0, description='')

    # Lightmap
    li_selection : bpy.props.EnumProperty(name='Unwrap', default='SEL_FACES', description='',
    items=[
    ('SEL_FACES', 'Selected_Faces', ''),
    ('ALL_FACES', 'All_Faces', '')
    ])

    li_share_texture_space : bpy.props.BoolProperty(name="share_texture_space", default=True, description='')
    li_new_uv_map : bpy.props.BoolProperty(name="new_uv_map", default=False, description='')
    li_new_image : bpy.props.BoolProperty(name="new_image", default=False, description='')
    li_image_size : bpy.props.IntProperty(name="image_size", default=128, min=64, soft_max=5000, description='')
    li_pack_quality : bpy.props.IntProperty(name="pack_quality", default=20, min=1, soft_max=48, description='')
    li_margin : bpy.props.FloatProperty(name="margin", default=0.05, min=0.0, soft_max=1.0, description='')


def _mode_switch(_mode):
    if bpy.context.active_object:
        bpy.ops.object.mode_set(mode=_mode)
    return{"Finished"}


class OBJECT_PT_TMG_UV_SelectOB(Operator):
    """Select object from scene and set it to active"""

    bl_idname = "tmg_uv.select_ob"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    name : bpy.props.StringProperty(name='UVMap')

    def execute(self, context):
        scene = context.scene
        tmg_uv_vars = scene.tmg_uv_vars
        bpy.context.view_layer.objects.active = bpy.data.objects[self.name]
        bpy.data.objects[self.name].select_set(True)         
        return {'FINISHED'}


class OBJECT_PT_TMG_UV_DeleteOB(Operator):
    """Delete object from scene"""

    bl_idname = "tmg_uv.delete_ob"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    name : bpy.props.StringProperty(name='UVMap')

    def execute(self, context):
        scene = context.scene
        tmg_uv_vars = scene.tmg_uv_vars

        bpy.context.view_layer.objects.active = bpy.data.objects[self.name]
        bpy.data.objects[self.name].select_set(True) 

        if bpy.context.view_layer.objects.active == bpy.data.objects[self.name]:
            bpy.context.view_layer.objects.active = None

        if bpy.data.objects[self.name]:
            bpy.data.objects.remove(bpy.data.objects[self.name], do_unlink=True)

        return {'FINISHED'}


class OBJECT_PT_TMG_UV_SelectUV(Operator):
    """Select uv layer from objects and set it to active"""

    bl_idname = "tmg_uv.select_uv"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    name : bpy.props.StringProperty(name='UVMap')

    def execute(self, context):
        sel_objs = [obj for obj in bpy.context.view_layer.objects.selected if obj.type == 'MESH']
        while len(sel_objs) >= 1:      
            ob = sel_objs.pop() 
            sel_uvs = [uv for uv in ob.data.uv_layers if uv.name == self.name]

            while len(sel_uvs) >= 1:      
                uv = sel_uvs.pop() 
                ob.data.uv_layers[uv.name].active = True         
        return {'FINISHED'}


class OBJECT_PT_TMG_UV_DeleteUV(Operator):
    """Delete uv from objects"""

    bl_idname = "tmg_uv.delete_uv"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    name : bpy.props.StringProperty(name='UVMap')

    def execute(self, context):
        sel_objs = [obj for obj in bpy.context.view_layer.objects.selected if obj.type == 'MESH']
        while len(sel_objs) >= 1:      
            ob = sel_objs.pop() 
            sel_uvs = [uv for uv in ob.data.uv_layers if uv.name == self.name]

            while len(sel_uvs) >= 1:      
                uv = sel_uvs.pop() 
                ob.data.uv_layers.remove(ob.data.uv_layers[uv.name])        
        return {'FINISHED'}


class OBJECT_PT_TMG_UV_DeleteAllUV(Operator):
    """Delete all uvs from objects"""

    bl_idname = "tmg_uv.delete_all_uv"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        sel_objs = [obj for obj in bpy.context.view_layer.objects.selected if obj.type == 'MESH']
        while len(sel_objs) >= 1:      
            ob = sel_objs.pop() 
            sel_uvs = [uv for uv in ob.data.uv_layers if ob.data.uv_layers.get(uv.name)]

            while len(sel_uvs) >= 1:      
                uv = sel_uvs.pop() 
                ob.data.uv_layers.remove(layer=uv)        
        return {'FINISHED'}


class OBJECT_PT_TMG_UV_AddUV(Operator):
    """Add uv to objects"""

    bl_idname = "tmg_uv.add_uv"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    name : bpy.props.StringProperty(name='UVMap')

    def execute(self, context):
        sel_objs = [obj for obj in bpy.context.view_layer.objects.selected if obj.type == 'MESH']
        while len(sel_objs) >= 1:      
            ob = sel_objs.pop() 
            ob.data.uv_layers.new(name=self.name)        
        return {'FINISHED'}


class OBJECT_PT_TMG_UV_RenameUV(Operator):
    """Rename uv layer on objects"""

    bl_idname = "tmg_uv.rename_uv"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    name : bpy.props.StringProperty(name='UVMap')
    rename : bpy.props.StringProperty(name='UVMap')

    def execute(self, context):
        sel_objs = [obj for obj in bpy.context.view_layer.objects.selected if obj.type == 'MESH']
        while len(sel_objs) >= 1:      
            ob = sel_objs.pop() 
            sel_uvs = [uv for uv in ob.data.uv_layers if uv.name == self.name]

            while len(sel_uvs) >= 1:      
                uv = sel_uvs.pop() 
                ob.data.uv_layers[uv.name].name = self.rename        
        return {'FINISHED'}


class OBJECT_PT_TMG_UV_ActiveRenderUV(Operator):
    """Set uv layer to active render on objects"""

    bl_idname = "tmg_uv.active_render_uv"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    name : bpy.props.StringProperty(name='UVMap')

    def execute(self, context):
        sel_objs = [obj for obj in bpy.context.view_layer.objects.selected if obj.type == 'MESH']
        while len(sel_objs) >= 1:      
            ob = sel_objs.pop() 
            sel_uvs = [uv for uv in ob.data.uv_layers if uv.name == self.name]

            while len(sel_uvs) >= 1:      
                uv = sel_uvs.pop() 
                ob.data.uv_layers[uv.name].active_render = True        
        return {'FINISHED'}


class OBJECT_PT_TMG_UV_Object_Panel(bpy.types.Panel):
    bl_idname = 'OBJECT_PT_tmg_uv_object_panel'
    bl_category = 'TMG'
    bl_label = 'UV Tools'
    bl_context = "objectmode"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        layout = self.layout
        

class OBJECT_PT_TMG_UV_Object_Panel_List(bpy.types.Panel):
    bl_idname = "OBJECT_PT_tmg_uv_object_panel_list"
    bl_label = ""
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_parent_id = "OBJECT_PT_tmg_uv_object_panel"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        layout = self.layout

        objs = []

        sel_objs = [obj for obj in bpy.context.view_layer.objects.selected if obj.type == 'MESH']
        while len(sel_objs) >= 1:      
            ob = sel_objs.pop() 
            objs.append(ob)

        layout.label(text="Objects : %s" %len(objs))
        

    def draw(self, context):
        scene = context.scene
        # props = scene.eevee
        # tmg_uv_vars = scene.tmg_uv_vars
        layout = self.layout
             
        objs = []

        sel_objs = [obj for obj in bpy.context.view_layer.objects.selected if obj.type == 'MESH']
        while len(sel_objs) >= 1:      
            ob = sel_objs.pop() 
            objs.append(ob)

        box = layout.box()
        col = box.column(align=False)
        row = col.row(align=True)

        if len(objs) < 1: 
            col.label(text="No Objects in Scene")

        # for ob in objs:
        while len(objs) >= 1:      
            ob = objs.pop() 
            row = col.row(align=True)

            # if bpy.context.space_data.objects == ob:
            if bpy.context.view_layer.objects.selected == ob:
                prop = row.operator("tmg_uv.select_ob", text=ob.name, emboss=False) #  icon="RESTRICT_SELECT_OFF",
            else:
                prop = row.operator("tmg_uv.select_ob", text=ob.name, emboss=True) #  icon="RESTRICT_SELECT_ON",
            prop.name = ob.name

            prop = row.operator("tmg_uv.delete_ob", text='', icon="TRASH")
            prop.name = ob.name    


# class OBJECT_PT_TMG_UV_Panel(bpy.types.Panel):
#     bl_idname = 'OBJECT_PT_tmg_uv_panel'
#     bl_label = 'UV Tools'
#     bl_space_type = "VIEW_3D"
#     bl_region_type = "UI"
#     bl_parent_id = "OBJECT_PT_tmg_uv_object_panel"
#     bl_options = {"DEFAULT_CLOSED"}

#     def draw(self, context):
#         layout = self.layout

            
class OBJECT_PT_TMG_UV_Panel_List(bpy.types.Panel):
    bl_idname = "OBJECT_PT_tmg_uv_panel_list"
    bl_label = ""
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_parent_id = "OBJECT_PT_tmg_uv_object_panel"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        layout = self.layout

        objs = []
        uvs = []

        sel_objs = [obj for obj in bpy.context.view_layer.objects.selected if obj.type == 'MESH']
        while len(sel_objs) >= 1:      
            ob = sel_objs.pop() 
            objs.append(ob)

            sel_uvs = [uv for uv in ob.data.uv_layers if uv.name not in uvs]
            while len(sel_uvs) >= 1:      
                uv = sel_uvs.pop() 
                uvs.append(uv.name)

        layout.label(text="UVs : %s" %len(uvs))
        prop = layout.operator("tmg_uv.add_uv", text='', icon="PLUS", emboss=True)
        prop = layout.operator("tmg_uv.delete_all_uv", text='', icon="X", emboss=True)
        

    def draw(self, context):
        scene = context.scene
        props = scene.eevee
        tmg_uv_vars = scene.tmg_uv_vars        

        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.
        layout = layout.column()
             
        objs = []
        uvs = []
        uvsData = []

        for ob in bpy.context.view_layer.objects.selected:
            if ob.type == "MESH":
                objs.append(ob)
                for uv in ob.data.uv_layers:
                    if uv.name not in uvs:
                        uvs.append(uv.name)
                        uvsData.append(uv)


        box = layout.box()
        col = box.column(align=False)
        row = col.row(align=True)  

        # row.label(text='Name')
        # row.prop(tmg_uv_vars, "uvName", text='Name')

        row = col.row(align=True)  

        if len(uvs) < 1: 
            col.label(text="No UVs on Objects")
        else:
            row.prop(tmg_uv_vars, "uvName", text='Name')
        
        for uv in uvs:
            row = col.row(align=True)

            if bpy.context.view_layer.objects.selected == uv:
                prop = row.operator("tmg_uv.select_uv", text=uv, emboss=False) #  icon="RESTRICT_SELECT_OFF",
            else:
                prop = row.operator("tmg_uv.select_uv", text=uv, emboss=True) #  icon="RESTRICT_SELECT_ON",
            prop.name = uv

            prop = row.operator("tmg_uv.rename_uv", text='', icon="GREASEPENCIL")
            prop.name = uv
            prop.rename = tmg_uv_vars.uvName

            for uvD in uvsData:
                if uvD.name == uv:
                    if  uvD.active_render:
                        prop = row.operator("tmg_uv.active_render_uv", text='', icon="RESTRICT_RENDER_OFF")
                    else:
                        prop = row.operator("tmg_uv.active_render_uv", text='', icon="RESTRICT_RENDER_ON")
                    prop.name = uv  

            prop = row.operator("tmg_uv.delete_uv", text='', icon="TRASH")
            prop.name = uv        


##### Edit Mode Panels #################################################################################


class EDIT_PT_TMG_UV_Unwrap(Operator):
    """Unwrap uvs of selected objects"""

    bl_idname = "tmg_uv.edit_unwrap_uv"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    name : bpy.props.StringProperty(name='UVMap')

    def draw(self, context):
        scene = context.scene
        tmg_uv_vars = scene.tmg_uv_vars        

        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.
        layout = layout.column()
             
        box = layout.box()
        col = box.column(align=False)
        row = col.row(align=True)  

        col.prop(tmg_uv_vars, 'unwrapTypes')

        col.prop(tmg_uv_vars, 'packMethod')

        if tmg_uv_vars.unwrapTypes == "Unwrap":
            # col.prop(tmg_uv_vars, 'selectAllFaces')
            col.prop(tmg_uv_vars, 'un_fill_holes')
            col.prop(tmg_uv_vars, 'un_correct_aspect')
            col.prop(tmg_uv_vars, 'un_use_subsurf_data')
            col.prop(tmg_uv_vars, 'un_margin')
            col.prop(tmg_uv_vars, 'clear_seams')
            col.prop(tmg_uv_vars, 'island_seams')
            
            col.prop(tmg_uv_vars, 'mark_sharp')
            if tmg_uv_vars.mark_sharp:
                col.prop(tmg_uv_vars, 'sharpness')

        elif tmg_uv_vars.unwrapTypes == "Smart_Project":
            col.prop(tmg_uv_vars, 'sp_angle_limit')
            col.prop(tmg_uv_vars, 'sp_margin')
            col.prop(tmg_uv_vars, 'sp_area_weight')
            # col.prop(tmg_uv_vars, 'selectAllFaces')
            col.prop(tmg_uv_vars, 'sp_correct_aspect')
            col.prop(tmg_uv_vars, 'sp_scale_to_bounds')
            col.prop(tmg_uv_vars, 'clear_seams')
            col.prop(tmg_uv_vars, 'island_seams')
            
            col.prop(tmg_uv_vars, 'mark_sharp')
            if tmg_uv_vars.mark_sharp:
                col.prop(tmg_uv_vars, 'sharpness')

        elif  tmg_uv_vars.unwrapTypes == "Lightmap":
            # col.prop(tmg_uv_vars, 'li_selection')
            # col.prop(tmg_uv_vars, 'selectAllFaces')
            col.prop(tmg_uv_vars, 'li_share_texture_space')
            col.prop(tmg_uv_vars, 'li_new_uv_map')
            col.prop(tmg_uv_vars, 'li_new_image')
            col.prop(tmg_uv_vars, 'li_image_size')
            col.prop(tmg_uv_vars, 'li_pack_quality')
            col.prop(tmg_uv_vars, 'li_margin')
            col.prop(tmg_uv_vars, 'clear_seams')
            col.prop(tmg_uv_vars, 'island_seams')
            
            # col.prop(tmg_uv_vars, 'mark_sharp')
            # if tmg_uv_vars.mark_sharp:
            #     col.prop(tmg_uv_vars, 'sharpness')

        else:
            col.label(text='No options')

    def execute(self, context):
        scene = context.scene
        tmg_uv_vars = scene.tmg_uv_vars

        # Make list of selected objects
        multi = bpy.context.selected_objects
        objs = [o for o in multi if o.data]

        # Select uv layer by name
        for ob in objs:
            _mode_switch('OBJECT')
            sel_uvs = [uv for uv in ob.data.uv_layers if uv.name == self.name]
            while len(sel_uvs) >= 1:      
                uv = sel_uvs.pop() 
                ob.data.uv_layers[uv.name].active = True   

        if tmg_uv_vars.packMethod == "individual":
            for ob in objs:
                me = ob.data

                _mode_switch('EDIT')

                bm = bmesh.from_edit_mesh(me)

                # Sync uv / face selection
                bpy.context.scene.tool_settings.use_uv_select_sync = True
                    
                # Set select mode to Edge
                bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
                    
                # Clear Seams
                if tmg_uv_vars.clear_seams:
                    # Select all uvs
                    bpy.ops.uv.select_all(action='SELECT')
                    bpy.ops.mesh.mark_seam(clear=True)
                    bpy.ops.uv.select_all(action='DESELECT')
                
                # Mark seams by sharp edges
                if tmg_uv_vars.mark_sharp:
                    bpy.ops.mesh.edges_select_sharp(sharpness=tmg_uv_vars.sharpness)
                    bpy.ops.mesh.mark_seam(clear=False)
                    bpy.ops.uv.select_all(action='DESELECT')

                # Loop over polygons in objects
                for p in ob.data.polygons:
                    bm.faces.ensure_lookup_table()
                    bm.faces[p.index].select = True
                      
                # Set select mode to Face
                bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
                
                if tmg_uv_vars.unwrapTypes == "Unwrap":
                    bpy.ops.uv.unwrap(
                        method = tmg_uv_vars.unwrapMethod, 
                        fill_holes = tmg_uv_vars.un_fill_holes, 
                        correct_aspect = tmg_uv_vars.un_correct_aspect, 
                        use_subsurf_data = tmg_uv_vars.un_use_subsurf_data, 
                        margin = tmg_uv_vars.un_margin)

                elif tmg_uv_vars.unwrapTypes == "Smart_Project":
                    bpy.ops.uv.smart_project(
                        angle_limit = tmg_uv_vars.sp_angle_limit, 
                        island_margin = tmg_uv_vars.sp_margin, 
                        area_weight = tmg_uv_vars.sp_area_weight,
                        correct_aspect = tmg_uv_vars.sp_correct_aspect, 
                        scale_to_bounds = tmg_uv_vars.sp_scale_to_bounds)

                elif  tmg_uv_vars.unwrapTypes == "Lightmap":                
                    bpy.ops.uv.lightmap_pack(
                        PREF_CONTEXT = tmg_uv_vars.li_selection, 
                        PREF_PACK_IN_ONE = tmg_uv_vars.li_share_texture_space,
                        PREF_NEW_UVLAYER = tmg_uv_vars.li_new_uv_map,
                        PREF_APPLY_IMAGE = tmg_uv_vars.li_new_image,
                        PREF_IMG_PX_SIZE = tmg_uv_vars.li_image_size,
                        PREF_BOX_DIV = tmg_uv_vars.li_pack_quality,
                        PREF_MARGIN_DIV = tmg_uv_vars.li_margin)
                
                # Set select mode to Edge
                bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
                
                # Mark island seams
                if tmg_uv_vars.island_seams:
                    bpy.ops.uv.seams_from_islands()
                
                # Deslect mesh
                bpy.ops.mesh.select_all(action='DESELECT')

                # Show the updates in the viewport
                bmesh.update_edit_mesh(me)
        else:
            _mode_switch('EDIT')
                
            # Sync uv / face selection
            bpy.context.scene.tool_settings.use_uv_select_sync = True
                
            # Set select mode to Edge
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
                
            # Select all uvs
            bpy.ops.uv.select_all(action='SELECT')

            # Clear Seams
            if tmg_uv_vars.clear_seams:
                bpy.ops.mesh.mark_seam(clear=True)
            
            # Mark seams by sharp edges
            if tmg_uv_vars.mark_sharp:
                bpy.ops.mesh.edges_select_sharp(sharpness=tmg_uv_vars.sharpness)
                bpy.ops.mesh.mark_seam(clear=False)
                
            # Set select mode to Face
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='FACE')
            
            if tmg_uv_vars.unwrapTypes == "Unwrap":
                bpy.ops.uv.unwrap(
                    method = tmg_uv_vars.unwrapMethod, 
                    fill_holes = tmg_uv_vars.un_fill_holes, 
                    correct_aspect = tmg_uv_vars.un_correct_aspect, 
                    use_subsurf_data = tmg_uv_vars.un_use_subsurf_data, 
                    margin = tmg_uv_vars.un_margin)

            elif tmg_uv_vars.unwrapTypes == "Smart_Project":
                bpy.ops.uv.smart_project(
                    angle_limit = tmg_uv_vars.sp_angle_limit, 
                    island_margin = tmg_uv_vars.sp_margin, 
                    area_weight = tmg_uv_vars.sp_area_weight,
                    correct_aspect = tmg_uv_vars.sp_correct_aspect, 
                    scale_to_bounds = tmg_uv_vars.sp_scale_to_bounds)

            elif  tmg_uv_vars.unwrapTypes == "Lightmap":                
                bpy.ops.uv.lightmap_pack(
                    PREF_CONTEXT = tmg_uv_vars.li_selection, 
                    PREF_PACK_IN_ONE = tmg_uv_vars.li_share_texture_space,
                    PREF_NEW_UVLAYER = tmg_uv_vars.li_new_uv_map,
                    PREF_APPLY_IMAGE = tmg_uv_vars.li_new_image,
                    PREF_IMG_PX_SIZE = tmg_uv_vars.li_image_size,
                    PREF_BOX_DIV = tmg_uv_vars.li_pack_quality,
                    PREF_MARGIN_DIV = tmg_uv_vars.li_margin)
            
            # Set select mode to Edge
            bpy.ops.mesh.select_mode(use_extend=False, use_expand=False, type='EDGE')
            
            # Mark island seams
            if tmg_uv_vars.island_seams:
                bpy.ops.uv.seams_from_islands()

            # Deslect mesh
            bpy.ops.mesh.select_all(action='DESELECT')

        return {'FINISHED'}


class EDIT_PT_TMG_UV_Panel(bpy.types.Panel):
    bl_idname = 'EDIT_PT_tmg_uv_panel'

    bl_space_type = "IMAGE_EDITOR"
    bl_label = 'UV Tools'
    bl_region_type = 'UI'
    bl_category = 'TMG'

    @classmethod
    def poll(cls, context):
        # ob = context.active_object
        sel_objs = [obj for obj in bpy.context.view_layer.objects.selected if obj.type == 'MESH']
        while len(sel_objs) >= 1:      
            ob = sel_objs.pop() 
            return ob and ob.mode == 'EDIT'

    def draw(self, context):
        layout = self.layout

            
class EDIT_PT_TMG_UV_Panel_List(bpy.types.Panel):
    bl_idname = "EDIT_PT_tmg_uv_panel_list"
    bl_label = ""
    bl_space_type = "IMAGE_EDITOR"
    bl_region_type = "UI"
    bl_parent_id = "EDIT_PT_tmg_uv_panel"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        layout = self.layout

        objs = []
        uvs = []

        sel_objs = [obj for obj in bpy.context.view_layer.objects.selected if obj.type == 'MESH']
        while len(sel_objs) >= 1:      
            ob = sel_objs.pop() 
            objs.append(ob)

            sel_uvs = [uv for uv in ob.data.uv_layers if uv.name not in uvs]
            while len(sel_uvs) >= 1:      
                uv = sel_uvs.pop() 
                uvs.append(uv.name)

        layout.label(text="UVs : %s" %len(uvs))
        prop = layout.operator("tmg_uv.add_uv", text='', icon="PLUS", emboss=True)
        prop = layout.operator("tmg_uv.delete_all_uv", text='', icon="X", emboss=True)
        

    def draw(self, context):
        scene = context.scene
        props = scene.eevee
        tmg_uv_vars = scene.tmg_uv_vars        

        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.
        layout = layout.column()
             
        objs = []
        uvs = []
        uvsData = []

        for ob in bpy.context.view_layer.objects.selected:
            if ob.type == "MESH":
                objs.append(ob)
                for uv in ob.data.uv_layers:
                    if uv.name not in uvs:
                        uvs.append(uv.name)
                        uvsData.append(uv)


        box = layout.box()
        col = box.column(align=False)
        row = col.row(align=True)  

        # row.label(text='Name')
        row.prop(tmg_uv_vars, "uvName", text='Name')

        row = col.row(align=True)  

        if len(uvs) < 1: 
            col.label(text="No UVs on Objects")
        
        for uv in uvs:
            row = col.row(align=True)

            if bpy.context.view_layer.objects.selected == uv:
                prop = row.operator("tmg_uv.select_uv", text=uv, emboss=False) #  icon="RESTRICT_SELECT_OFF",
            else:
                prop = row.operator("tmg_uv.select_uv", text=uv, emboss=True) #  icon="RESTRICT_SELECT_ON",
            prop.name = uv

            prop = row.operator("tmg_uv.rename_uv", text='', icon="GREASEPENCIL")
            prop.name = uv
            prop.rename = tmg_uv_vars.uvName

            prop = row.operator("tmg_uv.edit_unwrap_uv", text='', icon="MOD_UVPROJECT")
            prop.name = uv  

            for uvD in uvsData:
                if uvD.name == uv:
                    if  uvD.active_render:
                        prop = row.operator("tmg_uv.active_render_uv", text='', icon="RESTRICT_RENDER_OFF")
                    else:
                        prop = row.operator("tmg_uv.active_render_uv", text='', icon="RESTRICT_RENDER_ON")
                    prop.name = uv  

            prop = row.operator("tmg_uv.delete_uv", text='', icon="TRASH")
            prop.name = uv        


class EDIT_PT_TMG_UV_Unwrap_Settings_Panel(bpy.types.Panel):
    bl_idname = "EDIT_PT_tmg_uv_unwrap_settings_panel"
    bl_label = "Settings"
    bl_space_type = "IMAGE_EDITOR"
    bl_region_type = "UI"
    bl_parent_id = "EDIT_PT_tmg_uv_panel"
    bl_options = {"DEFAULT_CLOSED"}
        
    def draw(self, context):
        scene = context.scene
        tmg_uv_vars = scene.tmg_uv_vars        

        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.
        layout = layout.column()
             
        box = layout.box()
        col = box.column(align=False)
        row = col.row(align=True)  

        col.prop(tmg_uv_vars, 'unwrapTypes')
        col.prop(tmg_uv_vars, 'packMethod')


        if tmg_uv_vars.unwrapTypes == "Unwrap":
            # col.prop(tmg_uv_vars, 'selectAllFaces')
            col.prop(tmg_uv_vars, 'un_fill_holes')
            col.prop(tmg_uv_vars, 'un_correct_aspect')
            col.prop(tmg_uv_vars, 'un_use_subsurf_data')
            col.prop(tmg_uv_vars, 'un_margin')
            col.prop(tmg_uv_vars, 'clear_seams')
            col.prop(tmg_uv_vars, 'island_seams')

            col.prop(tmg_uv_vars, 'mark_sharp')
            if tmg_uv_vars.mark_sharp:
                col.prop(tmg_uv_vars, 'sharpness')

        elif tmg_uv_vars.unwrapTypes == "Smart_Project":
            col.prop(tmg_uv_vars, 'sp_angle_limit')
            col.prop(tmg_uv_vars, 'sp_margin')
            col.prop(tmg_uv_vars, 'sp_area_weight')
            # col.prop(tmg_uv_vars, 'selectAllFaces')
            col.prop(tmg_uv_vars, 'sp_correct_aspect')
            col.prop(tmg_uv_vars, 'sp_scale_to_bounds')
            col.prop(tmg_uv_vars, 'clear_seams')
            col.prop(tmg_uv_vars, 'island_seams')

            col.prop(tmg_uv_vars, 'mark_sharp')
            if tmg_uv_vars.mark_sharp:
                col.prop(tmg_uv_vars, 'sharpness')

        elif  tmg_uv_vars.unwrapTypes == "Lightmap":
            # col.prop(tmg_uv_vars, 'li_selection')
            # col.prop(tmg_uv_vars, 'selectAllFaces')
            col.prop(tmg_uv_vars, 'li_share_texture_space')
            col.prop(tmg_uv_vars, 'li_new_uv_map')
            col.prop(tmg_uv_vars, 'li_new_image')
            col.prop(tmg_uv_vars, 'li_image_size')
            col.prop(tmg_uv_vars, 'li_pack_quality')
            col.prop(tmg_uv_vars, 'li_margin')
            col.prop(tmg_uv_vars, 'clear_seams')
            col.prop(tmg_uv_vars, 'island_seams')
            
            # col.prop(tmg_uv_vars, 'mark_sharp')
            # if tmg_uv_vars.mark_sharp:
            #     col.prop(tmg_uv_vars, 'sharpness')

        else:
            col.label(text='No options')



