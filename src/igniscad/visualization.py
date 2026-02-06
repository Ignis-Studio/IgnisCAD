"""
Visualize models via YACV or exporting them to disk.
"""

import webbrowser
from typing import Literal

import build123d as bd

from igniscad import Model

def _show_yacv_model(model: Model) -> bool:
    """
    Try connecting Yet Another CAD Viewer (within the browser)，
    """
    try:
        from yacv_server import show as yacv_show
        target_obj = model
        yacv_show(target_obj, names=[model.name])

        url = "http://localhost:32323"
        print(f"✅ Sent to YACV (Check your browser, at {url})")
        webbrowser.open(url)
        input("✅ Press Enter to exit...")
        return True
    except Exception as e:
        print(f"⚠️ Failed to connect to YACV: {e}")
        return False



def _export_stl_file(model):
    """
    Try exporting the specified model to a *.stl file.
    """
    filename = f"{model.name}.stl"

    try:
        bd.export_stl(model, filename)
    except NameError:
        import build123d as bd_fallback
        bd_fallback.export_stl(model, filename)

    import os
    abs_path = os.path.abspath(filename)
    print(f"💾 Saved: {abs_path}")
    print("👉 You can open this file with Windows 3D Viewer.")

    try:
        os.startfile(abs_path)
    except:
        pass

def show(model: Model, mode: Literal['fallback', 'yacv', 'export'] = "fallback") -> None:
    """
    Visualize the specified model.
    Args:
        model (Model): The model to visualize
        mode (Literal['fallback', 'yacv', 'export'] = "fallback"): The method of visualization.
            "Fallback": to export the file when YACV is unavailable.
            "yacv": to visualize the model via Yet Another CAD Viewer.
            "export": to export the model to a *.stl file.
    """
    print(f"👀 Processing: {model.name}")
    match mode:
        case "fallback":
            if not _show_yacv_model(model):
                print("⚠️ Viewer not available. Exporting to disk...")
                _export_stl_file(model)
        case "yacv":
            _show_yacv_model(model)
        case "export":
            _export_stl_file(model)
        case _:
            raise ValueError("❌ Invalid visualization method.\nCan be: \n\tfallback, yacv, export.")


