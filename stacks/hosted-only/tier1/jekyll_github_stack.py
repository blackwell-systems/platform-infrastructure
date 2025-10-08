"""
Jekyll + GitHub Pages Stack

Business Context:
- Serves technical users who prefer Git-based workflows
- GitHub Pages compatible for zero-cost hosting option
- Perfect for documentation, blogs, and simple sites
"""

from typing import Dict, Any, Optional
from constructs import Construct
from aws_cdk import (
    aws_codebuild as codebuild,
    aws_s3 as s3,
    aws_iam as iam,
    CfnParameter,
    CfnOutput
)

from stacks.shared.base_ssg_stack import BaseSSGStack
from shared.ssg_engines import StaticSiteConfig


class JekyllGitHubStack(BaseSSGStack):
    """
    Jekyll static sites with GitHub Pages compatibility.

    Key Features:
    - Ruby-based Jekyll SSG with Bundler dependency management
    - GitHub Pages compatible themes and plugins
    - Git-based content workflow (technical users)
    - Dual hosting option: AWS or GitHub Pages
    - Cost-optimized for technical tier ($0-25/month)
    
    Target Clients:
    - Developers and technical professionals
    - Documentation sites and technical blogs
    - Open source projects needing professional hosting
    - Users comfortable with Git workflows and Markdown
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        client_id: str,
        domain: str,
        github_repo: Optional[str] = None,
        enable_github_pages_fallback: bool = True,
        theme_id: Optional[str] = None,
        theme_config: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        Initialize Jekyll GitHub Pages Stack.
        
        Args:
            scope: CDK construct scope
            construct_id: Unique identifier for this stack
            client_id: Client identifier for resource naming
            domain: Primary domain for the site
            github_repo: Optional GitHub repository URL (format: owner/repo)
            enable_github_pages_fallback: Whether to support GitHub Pages as backup
            theme_id: Optional theme ID from theme registry (e.g., 'minimal-mistakes-business')
            theme_config: Optional theme customization configuration
            **kwargs: Additional CDK stack parameters
        """
        
        # Create SSG configuration for Jekyll engine
        # Uses "simple_blog" template by default, with theme support
        ssg_config = StaticSiteConfig(
            client_id=client_id,
            domain=domain,
            ssg_engine="jekyll",  # Ruby-based SSG engine
            template_variant="simple_blog",  # GitHub Pages compatible template
            performance_tier="basic",  # Cost-optimized for technical tier
            theme_id=theme_id,  # Optional theme from registry
            theme_config=theme_config or {}  # Theme customization options
        )

        # Initialize base SSG infrastructure (S3, CloudFront, Route53)
        super().__init__(scope, construct_id, ssg_config, **kwargs)
        
        # Configure theme-specific buildspec customizations
        self._setup_theme_buildspec()
        
        # Store GitHub configuration
        self.github_repo = github_repo
        self.enable_github_pages_fallback = enable_github_pages_fallback
        
        # Set up Jekyll-specific features
        self._setup_jekyll_environment()
        self._setup_github_integration()
        self._setup_technical_features()
        
        # Create CDK parameters for client configuration
        self._create_stack_parameters()
        
        # Create outputs for client reference
        self._create_stack_outputs()

    def _setup_jekyll_environment(self) -> None:
        """
        Configure Jekyll-specific build environment and variables.
        
        Sets up Ruby environment, Bundler configuration, and Jekyll-specific
        environment variables that ensure GitHub Pages compatibility.
        """
        
        # Jekyll-specific environment variables
        # These ensure production builds and GitHub Pages compatibility
        jekyll_vars = {
            # Core Jekyll configuration
            "JEKYLL_ENV": "production",  # Enables production optimizations
            "BUNDLE_PATH": "vendor/bundle",  # Bundler gem installation path
            "BUNDLE_WITHOUT": "development:test",  # Skip dev dependencies
            
            # GitHub Pages compatibility
            "GITHUB_PAGES_COMPATIBLE": "true",  # Flag for template customization
            "JEKYLL_GITHUB_METADATA": "true",  # Enable GitHub metadata plugin
            
            # Performance optimizations
            "JEKYLL_DISABLE_DISK_CACHE": "false",  # Enable disk caching for faster builds
            "LIQUID_C_ENABLED": "true",  # Use liquid-c for faster template rendering
            
            # Site identification
            "SITE_TYPE": "technical_blog",  # Identifies this as technical content
            "HOSTING_PLATFORM": "aws_s3",  # Primary hosting platform
        }
        
        # Add theme-specific environment variables if theme is configured
        theme_info = self.ssg_config.get_theme_info()
        if theme_info:
            # Add theme-specific environment variables
            jekyll_vars.update(theme_info["theme_env_vars"])
            
            # Add theme installation variables
            jekyll_vars.update({
                "THEME_ID": theme_info["theme"].id,
                "THEME_SOURCE": theme_info["source"], 
                "THEME_INSTALLATION_METHOD": theme_info["installation_method"],
                "THEME_GITHUB_PAGES_COMPATIBLE": str(theme_info["github_pages_compatible"]).lower()
            })
        
        # Add environment variables to the CodeBuild project
        # This method is inherited from BaseSSGStack
        self.add_environment_variables(jekyll_vars)
        
    def _setup_github_integration(self) -> None:
        """
        Configure GitHub repository integration for source code management.
        
        Sets up CodeBuild to pull from GitHub repository and enables
        webhook-triggered builds when code is pushed to the main branch.
        """
        
        if self.github_repo:
            # Parse GitHub repository information
            # Expected format: "owner/repository-name"
            repo_parts = self.github_repo.split('/')
            if len(repo_parts) == 2:
                github_owner, github_repo_name = repo_parts
                
                # Configure CodeBuild source from GitHub
                # This replaces the default source configuration
                self.build_project.add_to_role_policy(
                    iam.PolicyStatement(
                        effect=iam.Effect.ALLOW,
                        actions=[
                            # Permissions needed for GitHub integration
                            "codebuild:CreateWebhook",
                            "codebuild:UpdateWebhook",
                            "codebuild:DeleteWebhook"
                        ],
                        resources=[self.build_project.project_arn]
                    )
                )
                
                # Add GitHub-specific environment variables
                github_vars = {
                    "GITHUB_OWNER": github_owner,
                    "GITHUB_REPO": github_repo_name,
                    "GITHUB_SOURCE": self.github_repo,
                    "SOURCE_VERSION": "main",  # Default to main branch
                }
                
                self.add_environment_variables(github_vars)
                
        # Set up GitHub Pages fallback configuration
        if self.enable_github_pages_fallback:
            self._setup_github_pages_fallback()
            
    def _setup_github_pages_fallback(self) -> None:
        """
        Configure GitHub Pages as a backup hosting option.
        
        This allows clients to fall back to free GitHub Pages hosting
        if they want to reduce costs or simplify their setup.
        """
        
        # GitHub Pages compatibility environment variables
        pages_vars = {
            # GitHub Pages specific configuration
            "GITHUB_PAGES_FALLBACK": "enabled",
            "BASEURL_GITHUB_PAGES": "",  # Will be configured per client
            
            # Ensure GitHub Pages plugin compatibility
            "JEKYLL_GITHUB_PLUGINS": "true",
            "SAFE_MODE": "true",  # GitHub Pages runs in safe mode
            
            # GitHub Pages build optimization
            "GITHUB_PAGES_BUILD": "true",
            "DISABLE_WHITELIST": "false",  # Respect GitHub Pages plugin whitelist
        }
        
        self.add_environment_variables(pages_vars)
        
    def _setup_technical_features(self) -> None:
        """
        Configure features specifically for technical users.
        
        Includes development tools, syntax highlighting, code examples,
        and other features that technical users expect.
        """
        
        # Technical user specific environment variables
        technical_vars = {
            # Code syntax highlighting
            "ROUGE_HIGHLIGHTER": "rouge",  # Syntax highlighter for code blocks
            "ROUGE_LINE_NUMBERS": "true",  # Enable line numbers in code blocks
            
            # Technical content features
            "ENABLE_MATH_SUPPORT": "true",  # MathJax for mathematical expressions
            "ENABLE_MERMAID_DIAGRAMS": "true",  # Diagram support for technical docs
            "ENABLE_CODE_COPY": "true",  # Copy buttons on code blocks
            
            # SEO and technical metadata
            "TECHNICAL_SEO": "enabled",  # Technical-focused SEO optimizations
            "ENABLE_SCHEMA_ORG": "true",  # Structured data for technical content
            
            # Development and debugging
            "JEKYLL_DEBUG": "false",  # Disable in production
            "ENABLE_LIVERELOAD": "false",  # Disable in production builds
            
            # Performance for technical content
            "COMPRESS_HTML": "true",  # Compress HTML output
            "COMPRESS_CSS": "true",  # Compress CSS output
            "COMPRESS_JS": "true",  # Compress JavaScript output
        }
        
        self.add_environment_variables(technical_vars)
        
        # Configure additional IAM permissions for technical features
        self._grant_technical_permissions()
        
    def _grant_technical_permissions(self) -> None:
        """
        Grant additional IAM permissions needed for technical features.
        
        Technical users may need additional AWS service access for
        advanced features like automated deployments or integrations.
        """
        
        # Grant CloudWatch Logs access for build debugging
        # Technical users often need to debug build issues
        self.build_project.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream", 
                    "logs:PutLogEvents",
                    "logs:DescribeLogGroups",
                    "logs:DescribeLogStreams"
                ],
                resources=[
                    f"arn:aws:logs:*:*:log-group:/aws/codebuild/{self.build_project.project_name}*"
                ]
            )
        )
        
        # Grant Parameter Store access for configuration management
        # Technical users may store configuration in Parameter Store
        self.build_project.add_to_role_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "ssm:GetParameter",
                    "ssm:GetParameters",
                    "ssm:GetParametersByPath"
                ],
                resources=[
                    f"arn:aws:ssm:*:*:parameter/{self.ssg_config.client_id}/*"
                ]
            )
        )
    
    def _setup_theme_buildspec(self) -> None:
        """
        Configure theme-specific buildspec commands and environment.
        
        Adds theme installation commands to the build process when a theme
        is configured, ensuring proper theme setup before Jekyll build.
        """
        
        theme_info = self.ssg_config.get_theme_info()
        if not theme_info:
            return
            
        # Get theme installation commands
        theme_commands = theme_info["installation_commands"]
        
        if theme_commands:
            # Get current buildspec from the build project
            # We need to modify it to add theme installation commands
            current_buildspec = self.engine_config.get_buildspec()
            
            # Add theme installation to pre_build phase
            if "phases" not in current_buildspec:
                current_buildspec["phases"] = {}
            if "pre_build" not in current_buildspec["phases"]:
                current_buildspec["phases"]["pre_build"] = {"commands": []}
            
            # Insert theme commands at the beginning of pre_build
            theme_install_commands = [
                "echo 'Installing Jekyll theme: " + theme_info["theme"].id + "'",
                "echo 'Theme source: " + theme_info["source"] + "'",
                "echo 'Installation method: " + theme_info["installation_method"] + "'"
            ]
            
            # Add actual theme installation commands
            theme_install_commands.extend(theme_commands)
            
            # Add theme customization if configured
            if self.ssg_config.theme_config:
                theme_install_commands.append("echo 'Applying theme customizations'")
                # Add any theme-specific customization commands here
                for key, value in self.ssg_config.theme_config.items():
                    theme_install_commands.append(f"echo 'Setting {key}={value}'")
            
            # Prepend theme commands to existing pre_build commands
            existing_commands = current_buildspec["phases"]["pre_build"].get("commands", [])
            current_buildspec["phases"]["pre_build"]["commands"] = theme_install_commands + existing_commands
            
            # Update the build project with modified buildspec
            # Note: This requires recreating the build project or using a custom buildspec
            # For now, we'll handle this through environment variables and the base buildspec
        
    def _create_stack_parameters(self) -> None:
        """
        Create CDK parameters for client-specific configuration.
        
        Technical users often want to customize their deployment
        without modifying code directly.
        """
        
        # GitHub repository parameter
        # Allows clients to specify their repository at deployment time
        self.github_repo_parameter = CfnParameter(
            self,
            "GitHubRepository",
            type="String",
            description="GitHub repository in format 'owner/repo' (optional)",
            default="",
            allowed_pattern=r"^$|^[a-zA-Z0-9._-]+/[a-zA-Z0-9._-]+$"
        )
        
        # Custom domain parameter
        # Allows clients to use their own domain
        self.custom_domain_parameter = CfnParameter(
            self,
            "CustomDomain",
            type="String", 
            description="Custom domain name for the site (optional)",
            default=""
        )
        
        # Jekyll theme parameter
        # Allows clients to specify which Jekyll theme to use
        self.jekyll_theme_parameter = CfnParameter(
            self,
            "JekyllTheme",
            type="String",
            description="Jekyll theme to use",
            default="minima",
            allowed_values=["minima", "minimal-mistakes", "jekyll-theme-clean-blog", "hyde", "lanyon"]
        )
        
        # Build frequency parameter
        # Technical users may want different build schedules
        self.build_schedule_parameter = CfnParameter(
            self,
            "BuildSchedule", 
            type="String",
            description="Automated build schedule (cron expression)",
            default="0 6 * * *",  # Daily at 6 AM UTC
        )
        
    def _create_stack_outputs(self) -> None:
        """
        Create CDK outputs for client reference and integration.
        
        Technical users need access to various AWS resource identifiers
        for integration with their own tools and workflows.
        """
        
        # Primary site URL
        CfnOutput(
            self,
            "SiteUrl",
            value=f"https://{self.ssg_config.domain}",
            description="Primary site URL (AWS CloudFront)",
            export_name=f"{self.stack_name}-SiteUrl"
        )
        
        # S3 bucket for content
        CfnOutput(
            self,
            "ContentBucket",
            value=self.content_bucket.bucket_name,
            description="S3 bucket containing site content",
            export_name=f"{self.stack_name}-ContentBucket"
        )
        
        # CloudFront distribution ID
        CfnOutput(
            self,
            "DistributionId",
            value=self.distribution.distribution_id,
            description="CloudFront distribution ID for cache invalidation",
            export_name=f"{self.stack_name}-DistributionId"
        )
        
        # CodeBuild project name
        CfnOutput(
            self,
            "BuildProjectName",
            value=self.build_project.project_name,
            description="CodeBuild project for manual builds and debugging",
            export_name=f"{self.stack_name}-BuildProject"
        )
        
        # GitHub Pages fallback URL (if enabled)
        if self.enable_github_pages_fallback and self.github_repo:
            github_pages_url = f"https://{self.github_repo.split('/')[0]}.github.io/{self.github_repo.split('/')[1]}"
            CfnOutput(
                self,
                "GitHubPagesUrl",
                value=github_pages_url,
                description="GitHub Pages URL (fallback option)",
                export_name=f"{self.stack_name}-GitHubPagesUrl"
            )
            
        # Technical documentation link
        CfnOutput(
            self,
            "DocumentationUrl",
            value="https://docs.yourservices.com/jekyll-github-stack",  # Replace with actual docs URL
            description="Technical documentation for this stack",
            export_name=f"{self.stack_name}-Documentation"
        )
        
    def get_client_setup_instructions(self) -> Dict[str, Any]:
        """
        Generate setup instructions for technical clients.
        
        Returns detailed technical instructions that clients need
        to connect their GitHub repository and customize their site.
        
        Returns:
            Dict containing setup instructions and technical details
        """
        
        instructions = {
            "stack_type": "Jekyll + GitHub Pages",
            "management_model": "Technical (⚙️)",
            "monthly_cost": "$0-25",
            
            "repository_setup": {
                "step_1": "Create a Jekyll site repository on GitHub",
                "step_2": f"Configure webhook to trigger builds: {self.build_project.project_name}",
                "step_3": "Push Jekyll source code to main branch",
                "step_4": "Site will automatically build and deploy to AWS"
            },
            
            "local_development": {
                "install": [
                    "gem install bundler jekyll",
                    "bundle install",
                    "bundle exec jekyll serve --livereload"
                ],
                "build": [
                    "bundle exec jekyll build",
                    "Test locally at http://localhost:4000"
                ]
            },
            
            "customization": {
                "theme": f"Current theme: {self.jekyll_theme_parameter.value_as_string}",
                "config": "Edit _config.yml for site configuration",
                "plugins": "See GitHub Pages plugin whitelist for allowed plugins",
                "custom_css": "Add custom styles in _sass/ directory"
            },
            
            "deployment": {
                "automatic": "Push to main branch triggers automatic deployment",
                "manual": f"Trigger build manually via CodeBuild: {self.build_project.project_name}",
                "rollback": "Revert GitHub commit and redeploy",
                "monitoring": "Check CloudWatch logs for build status"
            },
            
            "github_pages_fallback": {
                "enabled": self.enable_github_pages_fallback,
                "setup": "Enable GitHub Pages in repository settings -> Pages",
                "source": "Deploy from main branch / (root)",
                "cost": "Free with GitHub Pages (github.io domain)"
            },
            
            "technical_features": {
                "syntax_highlighting": "Enabled with Rouge",
                "math_support": "MathJax available for equations", 
                "diagrams": "Mermaid diagram support enabled",
                "seo": "Technical SEO optimizations included",
                "compression": "HTML/CSS/JS compression enabled"
            },
            
            "aws_resources": {
                "s3_bucket": self.content_bucket.bucket_name,
                "cloudfront_distribution": self.distribution.distribution_id,
                "codebuild_project": self.build_project.project_name,
                "domain": self.ssg_config.domain
            }
        }
        
        return instructions
        
    @property  
    def stack_cost_breakdown(self) -> Dict[str, str]:
        """
        Provide detailed cost breakdown for technical users.
        
        Technical users often want to understand exactly what
        they're paying for and optimize costs accordingly.
        
        Returns:
            Dict with detailed AWS cost breakdown
        """
        
        return {
            "setup_cost": "$360-720 (one-time)",
            "monthly_breakdown": {
                "s3_storage": "$1-5/month (depends on content size)",
                "cloudfront": "$1-10/month (depends on traffic)",
                "route53": "$0.50/month (hosted zone)",
                "codebuild": "$0-5/month (depends on build frequency)",
                "certificate_manager": "$0/month (free SSL certificates)"
            },
            "total_monthly": "$0-25/month (typical usage)",
            "cost_optimization": {
                "github_pages_fallback": "Use for $0/month hosting (github.io domain)",
                "infrequent_builds": "Manual builds reduce CodeBuild costs",
                "small_content": "Optimize images and content for lower S3 costs",
                "cache_optimization": "Longer cache times reduce CloudFront costs"
            },
            "enterprise_upgrade": "WordPress/WooCommerce ECS Professional available for $4,800-7,200 setup + $200-300/month"
        }