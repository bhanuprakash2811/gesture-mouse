"""
Verification script to check if all dependencies and components are properly installed.
"""
import importlib.util
import sys
import os

def check_python_version():
    """Check Python version."""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} (requires 3.8+)")
        return False

def check_package(package_name, import_name=None):
    """Check if a package is installed."""
    if import_name is None:
        import_name = package_name
    
    if importlib.util.find_spec(import_name) is not None:
        print(f"✅ {package_name}")
        return True
    print(f"❌ {package_name} (not installed)")
    return False

def check_file(filepath):
    """Check if a file exists."""
    if os.path.exists(filepath):
        print(f"✅ {filepath}")
        return True
    else:
        print(f"❌ {filepath} (not found)")
        return False

def check_cpp_module():
    """Check if C++ module is available."""
    try:
        import fast_math
        print("✅ fast_math (C++ module)")
        return True
    except ImportError:
        print("⚠️  fast_math (C++ module not found - optional, will use Python fallback)")
        return False

def main():
    """Run all checks."""
    print("=" * 60)
    print("Gesture Controlled Virtual Mouse - Installation Verification")
    print("=" * 60)
    print()
    
    all_ok = True
    
    print("Python Version:")
    all_ok &= check_python_version()
    print()
    
    print("Required Python Packages:")
    packages = [
        ("opencv-python", "cv2"),
        ("mediapipe", "mediapipe"),
        ("tensorflow", "tensorflow"),
        ("numpy", "numpy"),
        ("pyautogui", "pyautogui"),
        ("SpeechRecognition", "speech_recognition"),
        ("pyaudio", "pyaudio"),
        ("pybind11", "pybind11"),
        ("scikit-learn", "sklearn"),
        ("matplotlib", "matplotlib"),
        ("seaborn", "seaborn"),
        ("pandas", "pandas"),
    ]
    
    for pkg_name, import_name in packages:
        all_ok &= check_package(pkg_name, import_name)
    print()
    
    print("C++ Module:")
    check_cpp_module()
    print()
    
    print("Project Files:")
    files = [
        "src/main.py",
        "src/hand_tracking.py",
        "src/gesture_cnn.py",
        "src/voice_commands.py",
        "src/mouse_controller.py",
        "src/utils.py",
        "scripts/training/train_model.py",
        "scripts/training/collect_data.py",
    ]
    
    for filepath in files:
        all_ok &= check_file(filepath)
    print()
    
    print("Model:")
    if check_file("models/gesture_cnn.h5"):
        print("  (Model found - ready to run)")
    else:
        print("  (Model not found - run 'python -m scripts.training.train_model' to create)")
    print()
    
    print("=" * 60)
    if all_ok:
        print("✅ All required components are installed!")
        print("\nYou can now run the application:")
        print("  python src/main.py --mode hand")
    else:
        print("⚠️  Some components are missing.")
        print("\nPlease install missing packages:")
        print("  pip install -r requirements.txt")
        print("\nThe optional C++ source is not present in cpp/. Restore it before using the build scripts.")
    print("=" * 60)

if __name__ == '__main__':
    main()

