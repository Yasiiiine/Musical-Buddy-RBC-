# core/utils.py
import os

def asset_path(relative_path):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(base_dir, "..", "Assets", relative_path))
