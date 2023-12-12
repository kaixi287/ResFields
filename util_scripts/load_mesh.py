import trimesh
import os

mesh_dir = "../exp_owlii_benchmark/dysdf/dancer/dynerfResFields1234567/save/meshes/it400000"
# load mesh
meshes = [file for file in os.listdir(mesh_dir) if file.endswith(".ply")]
vertices = []
faces = []
for m in meshes:
    mesh = trimesh.load_mesh(os.path.join(mesh_dir, m))
    vertices.append(mesh.vertices.shape[0])
    faces.append(mesh.faces.shape[0])
print(f"Average number of vertices: {sum(vertices)/len(vertices)}")
print(f"Average number of faces: {sum(faces)/len(faces)}")