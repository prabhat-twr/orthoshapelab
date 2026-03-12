import open3d as o3d
import numpy as np
import os


def load_meshes(folder):

    meshes = []

    for f in os.listdir(folder):

        if f.endswith(".ply") or f.endswith(".stl"):

            mesh = o3d.io.read_triangle_mesh(os.path.join(folder, f))
            mesh.compute_vertex_normals()
            mesh.remove_duplicated_vertices()

            meshes.append(mesh)

    if len(meshes) == 0:
        raise RuntimeError("No meshes found")

    return meshes


def meshes_to_matrix(meshes):

    X = []

    for m in meshes:
        X.append(np.asarray(m.vertices).flatten())

    return np.array(X)