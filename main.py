import pickle
import numpy as np
from copy import deepcopy
import cv2

class HumanModel():
    def __init__(self, params=''):
        params = self.load_pkl(params)
        self.v_template = params['v_template']
        self.verts = deepcopy(self.v_template)
        self.weights = params['weights']
        self.faces = params['faces']
        self.J = params['bones']
        self.joint_template = self.J[:,:3,3]
        self.joint =deepcopy(self.joint_template)
        self.name = params['bone_name']
        self.parents = params['hierarchies']
        self.num_bone = len(self.J)

    def load_pkl(self, path):
        """"
        load pkl file
        """
        param = pickle.load(open(path, 'rb'),encoding='iso-8859-1')
        return param

    def save_to_obj(self, path):
        """
        Save the Human model into .obj file.
        Parameter:
        ---------
        path: Path to save.
        """
        with open(path, 'w') as fp:
            for v in self.verts:
                fp.write('v %f %f %f\n' % (v[0], v[1], v[2]))
            for f in self.faces + 1:
                fp.write('f %d %d %d\n' % (f[0], f[1], f[2]))
        print('save model to %s' %path)

    def pose_to_mat(self, pose):
        mats = []
        for p in pose:
            mat = np.eye(4)
            mat[:3,:3] = cv2.Rodrigues(tuple(p))[0]
            mats.append(mat)
        return np.array(mats)

    def linear_blending_skinning(self, pose, transl):
        self.joint = self.joint_template.copy()
        # The bones at the end are fixed
        pose[3] = np.array([0,0,0])

        rotation = self.pose_to_mat(pose)

        transform = []
        for i in range(self.num_bone):
            transform.append(np.eye(4))
        transform = np.array(transform)

        # skeleton deformation
        for i in range(self.num_bone):
            # current joint
            t = self.joint[i]
            parents_id = self.parents[i]
            # root joint
            if parents_id == -1:
                parent_trans = np.eye(4)
                self.joint[i] = t
            else:
                parent_trans = transform[parents_id].copy()

            # move to current joint
            parent_trans[:3,3] -= t
            # rotate around the current joint
            parent_trans = np.dot(rotation[i], parent_trans)
            # set current joint as origin
            parent_trans[:3,3] += t

            # 
            # the root joint of legs (12,16) are same as root joint (0)
            if i < self.num_bone-1 and i+1 != 12 and i+1 != 16:
                self.joint[i+1] = np.dot(parent_trans, np.insert(self.joint[i+1], 3, 1, axis=0))[:3]

            transform[i] = parent_trans

        # skinning
        # for i in range(len(self.v_template)):
        #     pos = np.zeros((3,))
        #     for w in range(len(self.weights[i])):
        #         if self.weights[i][w] < 1e-8:
        #             continue
        #         else:
        #             pos += np.dot(transform[w], np.insert(self.v_template[i], 3, 1, axis=0))[:3] * self.weights[i][w]
        #     temp = abs(self.v_template[i] - pos)
        #     self.verts[i] = pos

        T = np.dot(self.weights, transform.reshape(self.num_bone, -1)).reshape(-1,4,4)
        v_homo = np.insert(self.v_template, 3,1,axis=1)
        v_homo = np.matmul(T, np.expand_dims(v_homo, axis=-1))
        self.verts = np.squeeze(v_homo, axis=-1)[:,:3]

        self.verts += transl
        self.joint += transl

if __name__ == "__main__":
    
    model = HumanModel('params.pkl')
    # set translation
    transl = np.array([10,0,0])
    # set pose
    pose = np.random.rand(model.num_bone, 3) * 0.0
    pose[9] = np.array([0,0.3,0])
    pose[5] = np.array([0,0.5,0])
    pose[13] = np.array([0.5,0.0,0])

    # perform skinning
    model.linear_blending_skinning(pose, transl)
    
    model.save_to_obj('test.obj')
