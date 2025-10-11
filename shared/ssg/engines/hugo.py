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
                name="documentation",
                description="Technical documentation sites with advanced navigation",
                use_cases=["api_docs", "technical_manuals", "knowledge_bases", "documentation_sites"],
                repo_url="https://github.com/your-templates/hugo-documentation",
                customization_points=[
                    "search_integration",
                    "navigation_tree",
                    "code_highlighting",
                    "multi_language_support",
                ],
                demo_url="https://demo.yourservices.com/hugo-documentation",
            ),
            SSGTemplate(
                name="performance_blog",
                description="High-performance blog sites with technical focus",
                use_cases=[
                    "technical_blogs",
                    "news_sites",
                    "content_marketing",
                    "fast_loading_blogs",
                ],
                repo_url="https://github.com/your-templates/hugo-performance-blog",
                customization_points=[
                    "analytics_integration",
                    "seo_optimization",
                    "social_sharing",
                    "comment_systems",
                ],
                demo_url="https://demo.yourservices.com/hugo-performance-blog",
            ),
            SSGTemplate(
                name="technical_portfolio",
                description="Developer portfolio sites with project showcases",
                use_cases=[
                    "developer_portfolios",
                    "academic_sites",
                    "professional_showcases",
                    "project_galleries",
                ],
                repo_url="https://github.com/your-templates/hugo-technical-portfolio",
                customization_points=[
                    "project_gallery",
                    "cv_sections",
                    "contact_forms",
                    "portfolio_showcase",
                ],
                demo_url="https://demo.yourservices.com/hugo-technical-portfolio",
            ),
        ]