"""Check that python package, node package, and openapi schema versions are in sync."""
import re
from pathlib import Path

root = Path(__file__).parent.parent

# check python package versions
pyproject_toml = root / "pyproject.toml"
pyproject_toml_text = pyproject_toml.read_text()
pyproject_toml_version = re.search(r'version = "(.*)"', pyproject_toml_text).group(1)

package_json = root / "app" / "package.json"
package_json_text = package_json.read_text()
package_json_version = re.search(r'"version": "(.*)"', package_json_text).group(1)

# also check the lock file
package_lock_json = root / "app" / "package-lock.json"
package_lock_json_text = package_lock_json.read_text()
package_lock_json_version = re.search(
    r'"version": "(.*)"', package_lock_json_text
).group(1)

# check openapi schema versions

openapi_schema = root / "app" / "static" / "openapi" / "openapi.yaml"
openapi_schema_text = openapi_schema.read_text()
openapi_schema_version = re.search(r"version: (.*)", openapi_schema_text).group(1)

versions = [
    pyproject_toml_version,
    package_json_version,
    package_lock_json_version,
    openapi_schema_version,
]

# check all versions are the same
assert len(set(versions)) == 1, f"Versions are not in sync {versions}"
print(f"Versions are in sync {versions[0]}")
