"""
Abstract Base SSG Engine Configuration

Defines the interface that all SSG engine implementations must follow.
Provides common functionality for CodeBuild integration and buildspec generation.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List

from aws_cdk import aws_codebuild as codebuild

from .core_models import BuildCommand, SSGTemplate


class SSGEngineConfig(ABC):
    """Abstract base class for SSG engine configurations"""

    def __init__(self, template_variant: str = "default"):
        self.template_variant = template_variant

    @property
    @abstractmethod
    def engine_name(self) -> str:
        """Name of the SSG engine"""
        pass

    @property
    def ssg_engine(self) -> str:
        """Compatibility property for test expectations - returns engine_name"""
        return self.engine_name

    @property
    @abstractmethod
    def runtime_version(self) -> str:
        """Node.js or other runtime version"""
        pass

    @property
    @abstractmethod
    def install_commands(self) -> List[str]:
        """Commands to install dependencies"""
        pass

    @property
    @abstractmethod
    def build_commands(self) -> List[BuildCommand]:
        """Commands to build the site"""
        pass

    @property
    @abstractmethod
    def output_directory(self) -> str:
        """Directory containing built site files"""
        pass

    @property
    @abstractmethod
    def optimization_features(self) -> Dict[str, Any]:
        """Engine-specific optimization settings"""
        pass

    @property
    @abstractmethod
    def available_templates(self) -> List[SSGTemplate]:
        """Templates available for this engine"""
        pass

    def get_codebuild_environment(self) -> codebuild.BuildEnvironment:
        """Generate CodeBuild environment for this engine"""
        return codebuild.BuildEnvironment(
            build_image=codebuild.LinuxBuildImage.STANDARD_7_0,
            environment_variables={
                "SSG_ENGINE": codebuild.BuildEnvironmentVariable(
                    value=self.engine_name
                ),
                "TEMPLATE_VARIANT": codebuild.BuildEnvironmentVariable(
                    value=self.template_variant
                ),
                "OUTPUT_DIR": codebuild.BuildEnvironmentVariable(
                    value=self.output_directory
                ),
            },
        )

    def get_buildspec(self) -> Dict[str, Any]:
        """Generate CodeBuild buildspec for this engine"""
        # Handle different runtime types
        runtime_versions = {}
        if self.runtime_version.startswith("nodejs-"):
            runtime_versions["nodejs"] = self.runtime_version.split("nodejs-")[1]
        elif self.runtime_version.startswith("golang-"):
            runtime_versions["golang"] = self.runtime_version.split("golang-")[1]
        elif self.runtime_version.startswith("ruby-"):
            runtime_versions["ruby"] = self.runtime_version.split("ruby-")[1]

        install_phase = {
            "runtime-versions": runtime_versions,
            "commands": self.install_commands,
        }

        build_phase = {"commands": [cmd.command for cmd in self.build_commands]}

        return {
            "version": "0.2",
            "phases": {"install": install_phase, "build": build_phase},
            "artifacts": {"files": ["**/*"], "base-directory": self.output_directory},
        }