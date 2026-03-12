import numpy as np
import open3d as o3d
import open3d.visualization.gui as gui
import open3d.visualization.rendering as rendering

from .mesh_loader import load_meshes, meshes_to_matrix
from .pca_model import PCAShapeModel


def select_folder():

    app = gui.Application.instance
    app.initialize()

    window = app.create_window("Select Shape Folder", 400, 200)

    selected_folder = {"path": None}

    def on_folder_selected(path):
        selected_folder["path"] = path
        window.close()

    def on_cancel():
        app.quit()

    dlg = gui.FileDialog(gui.FileDialog.OPEN_DIR, "Select Mesh Folder", window.theme)
    dlg.set_on_done(on_folder_selected)
    dlg.set_on_cancel(on_cancel)

    window.show_dialog(dlg)

    app.run()

    return selected_folder["path"]


def run():

    folder = select_folder()

    if folder is None:
        raise RuntimeError("No folder selected")

    print("Loading meshes from:", folder)

    meshes = load_meshes(folder)

    faces = meshes[0].triangles

    X = meshes_to_matrix(meshes)

    model = PCAShapeModel(X)

    n_modes = len(model.eigenvalues)

    coeffs = np.zeros(n_modes)

    display_mode = "mesh"

    camera_initialized = False


    def reconstruct():
        return model.reconstruct(coeffs)


    app = gui.Application.instance
    app.initialize()

    window = app.create_window("OrthoShapeLab PCA Viewer", 1400, 900)

    scene = gui.SceneWidget()
    scene.scene = rendering.Open3DScene(window.renderer)

    scene.scene.set_background([0.1, 0.1, 0.1, 1])

    window.add_child(scene)

    panel = gui.Vert(10, gui.Margins(10, 10, 10, 10))

    panel.add_child(gui.Label("PCA Shape Controls"))


    var = model.variance_ratio

    panel.add_child(gui.Label("Variance Explained"))

    for i in range(n_modes):
        panel.add_child(gui.Label(f"Mode {i+1}: {var[i]*100:.2f}%"))

    panel.add_child(gui.Label(""))


    def update_mesh():

        nonlocal camera_initialized

        vertices = reconstruct()

        scene.scene.clear_geometry()

        if display_mode == "mesh":

            mesh = o3d.geometry.TriangleMesh()

            mesh.vertices = o3d.utility.Vector3dVector(vertices)
            mesh.triangles = faces

            mesh.compute_vertex_normals()

            mat = rendering.MaterialRecord()
            mat.shader = "defaultLit"

            scene.scene.add_geometry("mesh", mesh, mat)

            bbox = mesh.get_axis_aligned_bounding_box()

        else:

            pcd = o3d.geometry.PointCloud()
            pcd.points = o3d.utility.Vector3dVector(vertices)

            mat = rendering.MaterialRecord()
            mat.shader = "defaultUnlit"
            mat.point_size = 3.0

            scene.scene.add_geometry("points", pcd, mat)

            bbox = pcd.get_axis_aligned_bounding_box()

        if not camera_initialized:

            scene.setup_camera(60, bbox, bbox.get_center())

            camera_initialized = True


    sliders = []


    def slider_callback(idx):

        def cb(val):
            coeffs[idx] = val
            update_mesh()

        return cb


    for i in range(n_modes):

        panel.add_child(gui.Label(f"PCA Mode {i+1}"))

        slider = gui.Slider(gui.Slider.DOUBLE)

        slider.set_limits(-3, 3)

        slider.set_on_value_changed(slider_callback(i))

        panel.add_child(slider)

        sliders.append(slider)


    def random_shape():

        nonlocal coeffs

        coeffs = np.random.normal(0, 1, n_modes)

        for i, s in enumerate(sliders):
            s.double_value = coeffs[i]

        update_mesh()


    random_btn = gui.Button("Random Shape")

    random_btn.set_on_clicked(random_shape)

    panel.add_child(random_btn)


    def show_mean_shape():

        nonlocal coeffs

        coeffs = np.zeros(n_modes)

        for s in sliders:
            s.double_value = 0

        update_mesh()


    mean_btn = gui.Button("Mean Shape")

    mean_btn.set_on_clicked(show_mean_shape)

    panel.add_child(mean_btn)


    def toggle_pointcloud():

        nonlocal display_mode

        if display_mode == "mesh":
            display_mode = "pointcloud"
        else:
            display_mode = "mesh"

        update_mesh()


    toggle_btn = gui.Button("Toggle Point Cloud / Mesh")

    toggle_btn.set_on_clicked(toggle_pointcloud)

    panel.add_child(toggle_btn)


    window.add_child(panel)


    def on_layout(ctx):

        r = window.content_rect

        panel_width = 320

        scene.frame = gui.Rect(r.x, r.y, r.width - panel_width, r.height)

        panel.frame = gui.Rect(
            r.get_right() - panel_width,
            r.y,
            panel_width,
            r.height
        )


    window.set_on_layout(on_layout)

    update_mesh()

    app.run()