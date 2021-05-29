import bpy
import numpy as np
import os
import pickle

def save_pkl(path, result):
    """"
    save pkl file
    """
    folder = os.path.dirname(path)
    if not os.path.exists(folder):
        os.makedirs(folder)

    with open(path, 'wb') as result_file:
        pickle.dump(result, result_file, protocol=2)

def get_bone_matrix(a):
    bone_mat = []
    bone_name = []
    for bone in a.pose.bones:
        bone_name.append(bone.name)
        bone_mat.append(np.array(bone.matrix))
    return np.array(bone_mat), bone_name

def get_vertices(me, ob_main):
    me_verts = me.vertices[:]
    if bpy.app.version[1] > 80:
        vertices = [(ob_main.matrix_world @ me_verts.co).to_tuple() for me_verts in me_verts]
    elif bpy.app.version[1] > 70:
        vertices = [(ob_main.matrix_world * me_verts.co).to_tuple() for me_verts in me_verts]
    return np.array(vertices)

def get_faces(me):
    me_verts = me.vertices[:]
    face_index_pairs = [(face, index) for index, face in enumerate(me.polygons)]
    face_index = []
    for f, f_index in face_index_pairs:
        f_v = [(vi, me_verts[v_idx], l_idx)
            for vi, (v_idx, l_idx) in enumerate(zip(f.vertices, f.loop_indices))]
        t = []
        for vi, v, li in f_v:
            t.append(v.index)
        face_index.append(t)
    return np.array(face_index)

def get_weights(me, num_bone):
    me_verts = me.vertices[:]
    weights = []
    for v in me_verts:
        temp = np.zeros((num_bone,))
        for g in v.groups:
            temp[g.group] = g.weight
        # we can not get the weight less than a threshold
        # so, normalize weights
        temp = temp/np.sum(temp)
        weights.append(temp)
    return np.array(weights, dtype=np.float64)

if __name__ == "__main__":
    # the name of the skeleton and the mesh are defined by users
    data = {}
    skeleton = "Armature"
    mesh = "template"
    # the skeleton hierarchy is defined by users
    # you can change the order according to your skeleton
    data['hierarchies'] = [-1,0,1,2,1,4,5,6,1,8,9,10,0,12,13,14,0,16,17,18]

    a = bpy.data.objects[skeleton]
    ob_main = bpy.data.objects[mesh]
    if bpy.app.version[1] > 80:
        # the version of current blender > 80
        depsgraph = bpy.context.evaluated_depsgraph_get()
        me = ob_main.to_mesh(preserve_all_data_layers=True, depsgraph=depsgraph)
    elif bpy.app.version[1] > 70:
        depsgraph = bpy.context.scene
        me = ob_main.to_mesh(depsgraph, True, 'RENDER')
        

    # get bones
    data['bones'], data['bone_name'] = get_bone_matrix(a)

    # get vertices
    data['v_template'] = get_vertices(me, ob_main)

    # get faces
    data['faces'] = get_faces(me)

    # get weights
    data['weights'] = get_weights(me, len(data['bones']))

    save_pkl('./params.pkl', data)
