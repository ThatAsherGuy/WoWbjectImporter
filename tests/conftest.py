def pytest_addoption(parser):
    parser.addoption(
        "--blender-executable",
        "--blender-exe",
        action='store',
        default="blender"
    )

def pytest_html_report_title(report):
    report.title = "WoWbject Importer Test Report"
