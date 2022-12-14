def cv2_custom_build_init(site_packages_path="/usr/local/lib/python3.9/site-packages"):
    import pathlib, sys
    site_path = pathlib.Path(site_packages_path)
    cv2_libs_dir = (
        site_path / "cv2" / f"python-{sys.version_info.major}.{sys.version_info.minor}"
    )
    print(cv2_libs_dir)
    cv2_libs = sorted(cv2_libs_dir.glob("*.so"))
    if len(cv2_libs) == 1:
        print("INSERTING:", cv2_libs[0].parent)
        sys.path.insert(1, str(cv2_libs[0].parent))