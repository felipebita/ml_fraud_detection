# debug_mypy_env.py
import subprocess
import sys
from importlib.metadata import PackageNotFoundError, version

print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")


def get_pkg_version(package_name):
    try:
        return version(package_name)
    except PackageNotFoundError:
        return "Not installed"


print(f"mypy version: {get_pkg_version('mypy')}")
print(f"pandas version: {get_pkg_version('pandas')}")
print(f"pandas-stubs version: {get_pkg_version('pandas-stubs')}")
print(f"duckdb version: {get_pkg_version('duckdb')}")

# Check mypy command output as well, as it can be revealing
try:
    result = subprocess.run(
        ["mypy", "--version"], capture_output=True, text=True, check=True
    )
    print(f"'mypy --version' output: {result.stdout.strip()}")
except (subprocess.CalledProcessError, FileNotFoundError) as e:
    print(f"Could not run 'mypy --version': {e}")
