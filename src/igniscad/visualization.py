"""
Visualize models via YACV or exporting them to disk.
"""

import webbrowser
import build123d as bd


def show(item):
    """
    Try connecting Yet Another CAD Viewer (within the browser)，
    If failed: fallback to save and open the *.stl file.
    """
    label = item.name or "Model"
    print(f"👀 Processing: {label}")

    # Try connecting Yet Another CAD Viewer (YACV)
    try:
        from yacv_server import show as yacv_show
        target_obj = item
        yacv_show(target_obj, names=[label])

        url = "http://localhost:32323"
        print(f"✅ Sent to YACV (Check your browser, at {url})")
        webbrowser.open(url)
        input("✅ Press Enter to exit...")
        return
    except Exception as e:
        print(f"⚠️ Failed to connect to YACV: {e}")

    # If failed: fallback to save and open the *.stl file.
    print("⚠️ Viewer not available. Exporting to disk...")
    filename = f"{label}.stl"

    try:
        bd.export_stl(item, filename)
    except NameError:
        import build123d as bd_fallback
        bd_fallback.export_stl(item, filename)

    import os
    abs_path = os.path.abspath(filename)
    print(f"💾 Saved: {abs_path}")
    print("👉 You can open this file with Windows 3D Viewer.")

    try:
        os.startfile(abs_path)
    except:
        pass
