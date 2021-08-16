def pytest_addoption(parser):
    parser.addoption(
        "--blender-executable",
        "--blender-exe",
        action='store',
        default="blender"
    )
