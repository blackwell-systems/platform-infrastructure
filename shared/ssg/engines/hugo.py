"""
Hugo SSG Engine Configuration

Defines the Hugo static site generator engine with its specific
build commands, templates, and optimization features.
"""

from typing import List, Dict, Any

from ..base_engine import SSGEngineConfig
from ..core_models import BuildCommand, SSGTemplate


class HugoConfig(SSGEngineConfig):
    """Hugo SSG engine configuration"""

    @property
    def engine_name(self) -> str:
        return "hugo"

    @property
    def runtime_version(self) -> str:
        return "golang-1.21"  # Hugo is Go-based

    @property
    def install_commands(self) -> List[str]:
        return [
            "wget https://github.com/gohugoio/hugo/releases/download/v0.121.0/hugo_extended_0.121.0_Linux-64bit.tar.gz",
            "tar -xzf hugo_extended_0.121.0_Linux-64bit.tar.gz",
            "chmod +x hugo",
            "sudo mv hugo /usr/local/bin/",
        ]

    @property
    def build_commands(self) -> List[BuildCommand]:
        return [
            BuildCommand(
                name="build_site",
                command="hugo --minify --gc",
                environment_vars={"HUGO_ENV": "production"},
            ),
            BuildCommand(
                name="optimize_images",
                command="hugo --minify --gc --enableGitInfo",
                environment_vars={"HUGO_ENV": "production"},
            ),
        ]

    @property
    def output_directory(self) -> str:
        return "public"

    @property
    def optimization_features(self) -> Dict[str, Any]:
        return {
            "extremely_fast_builds": True,
            "built_in_minification": True,
            "image_processing": True,
            "asset_bundling": True,
            "template_caching": True,
            "incremental_builds": False,  # Hugo rebuilds everything but very fast
            "build_performance": "extremely_fast",
        }

    @property
    def available_templates(self) -> List[SSGTemplate]:
        return [
            SSGTemplate(
                name="corporate_clean",
                description="Clean corporate design with powerful content management",
                use_cases=["corporate_sites", "large_content_sites", "multi_language"],
                repo_url="https://github.com/your-templates/hugo-corporate-clean",
                customization_points=[
                    "theme_colors",
                    "layout_options",
                    "content_sections",
                    "navigation",
                ],
                demo_url="https://demo.yourservices.com/hugo-corporate",
            ),
            SSGTemplate(
                name="content_publisher",
                description=(
                    "Content-heavy site with blog, resources, and knowledge base"
                ),
                use_cases=[
                    "content_sites",
                    "blogs",
                    "documentation",
                    "knowledge_bases",
                ],
                repo_url="https://github.com/your-templates/hugo-content-publisher",
                customization_points=[
                    "content_taxonomy",
                    "search_functionality",
                    "author_profiles",
                    "content_types",
                ],
                demo_url="https://demo.yourservices.com/hugo-content",
            ),
        ]