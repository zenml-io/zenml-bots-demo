"""Container settings shared by every pipeline."""

from zenml.config import DockerSettings
from zenml.config.docker_settings import (
    DockerBuildConfig,
    DockerBuildOptions,
    PythonPackageInstaller,
)

# Images are often built on Apple Silicon laptops but run on AMD64 cluster
# nodes, so the platform is pinned explicitly.
DOCKER_SETTINGS = DockerSettings(
    requirements="requirements.txt",
    python_package_installer=PythonPackageInstaller.UV,
    build_config=DockerBuildConfig(
        build_options=DockerBuildOptions(platform="linux/amd64")
    ),
)
