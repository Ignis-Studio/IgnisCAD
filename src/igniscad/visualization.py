"""
Visualize models via YACV or exporting them to disk.
"""

import webbrowser, os
from typing import Literal

import build123d as bd

from igniscad import Model
from igniscad.helpers.logger_handler import init_sub_logger, get_logger

init_sub_logger(__name__)

def _show_yacv_model(model: Model, force: bool) -> bool:
    """
    Try connecting Yet Another CAD Viewer (within the browser).

    Args:
        model (Model): The model to visualize.
        force (bool): whether to fallback or not.
    """
    from yacv_server import show as yacv_show
    target_obj = model
    yacv_show(target_obj, names=[model.name])

    url = "http://localhost:32323"
    print(f"Sent to YACV (Check your browser, at {url})")

    if not (webbrowser.open(url) or force):
        return False  # Fallback
    else:
        get_logger(__name__).error("Browser unavailable.(try using fallback mode)")

    input("Press Enter to exit...")
    return True


def _export_stl_file(model: Model) -> None:
    """
    Try exporting the specified model to a *.stl file.

    Args:
        model (Model): The model to export.
    """
    filename = f"{model.name}.stl"
    model.part = model.wrap_result(model.part) # Necessary: wrap everything into compound.
    bd.export_stl(model.part, filename)
    abs_path = os.path.abspath(filename)
    print(f"Saved: {abs_path}")
    print("You can open this file with 3D Viewer Applications.")

    from contextlib import suppress
    with suppress(Exception):
        os.startfile(abs_path)
    return

def show(model: Model, mode: Literal['fallback', 'yacv', 'export'] = "fallback") -> None:
    """
    Visualize the specified model.

    Args:
        model (Model): The model to visualize.
        mode (Literal['fallback', 'yacv', 'export'] = "fallback"): The method of visualization.
            "Fallback": to export the file when YACV is unavailable.
            "yacv": to visualize the model via Yet Another CAD Viewer.
            "export": to export the model to a *.stl file.
    """
    get_logger(__name__).info(f"Processing model: {model.name}")
    match mode:
        case "fallback":
            if not _show_yacv_model(model, force=False):
                get_logger(__name__).warning("Viewer not available. Exporting to disk...")
                _export_stl_file(model)
        case "yacv":
            _show_yacv_model(model, force=True)
        case "export":
            _export_stl_file(model)

    return
