"""
Theme Models for SSG Theme Registry

Pydantic models defining theme metadata, installation methods,
and configuration options for all supported SSG engines.
"""

from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator
from enum import Enum


class ThemeInstallMethod(str, Enum):
    """
    Supported theme installation methods across different SSG engines.
    
    Different SSG engines support different theme installation approaches.
    This enum captures the practical installation methods we support.
    """
    
    # Jekyll-specific installation methods
    REMOTE_THEME = "remote_theme"      # Jekyll remote_theme (GitHub Pages compatible)
    GEM_THEME = "gem_theme"            # Gem-based theme (not used in our system)
    GIT_CLONE = "git_clone"            # Clone and copy theme files
    
    # Universal installation methods  
    TEMPLATE_REPO = "template_repo"    # Complete template repository
    FORK_REPO = "fork_repo"           # Fork repository and customize
    NPM_PACKAGE = "npm_package"        # NPM-based theme (Astro, Gatsby, Next.js)
    
    # Hugo-specific
    GIT_SUBMODULE = "git_submodule"   # Hugo themes as git submodules
    HUGO_MODULE = "hugo_module"        # Hugo modules system
    
    # Custom/manual installation
    MANUAL_SETUP = "manual_setup"      # Manual file copying and configuration


class Theme(BaseModel):
    """
    Comprehensive theme definition for SSG engines.
    
    Defines theme metadata, installation requirements, compatibility,
    and customization options for any supported SSG engine.
    """
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        json_schema_extra={
            "examples": [
                {
                    "id": "minimal-mistakes-business",
                    "name": "Minimal Mistakes - Business",
                    "description": "Professional Jekyll theme with clean design and business focus",
                    "engine": "jekyll",
                    "installation_method": "remote_theme",
                    "source": "mmistakes/minimal-mistakes@4.27.3",
                    "required_plugins": ["jekyll-include-cache", "jekyll-paginate"],
                    "github_pages_compatible": True,
                    "demo_url": "https://mmistakes.github.io/minimal-mistakes/",
                    "categories": ["business", "professional", "portfolio"],
                    "customization_options": {
                        "skins": ["default", "dark", "mint"],
                        "author_profile": True,
                        "navigation": True
                    }
                }
            ]
        }
    )
    
    # Core theme identification
    id: str = Field(
        ...,
        description="Unique theme identifier (kebab-case)",
        pattern=r"^[a-z0-9-]+$",
        min_length=3,
        max_length=50
    )
    
    name: str = Field(
        ...,
        description="Human-readable theme name",
        min_length=3,
        max_length=100
    )
    
    description: str = Field(
        ...,
        description="Detailed theme description and features",
        min_length=10,
        max_length=500
    )
    
    # Engine compatibility
    engine: Literal["jekyll", "hugo", "astro", "eleventy", "nextjs", "nuxt", "gatsby"] = Field(
        ...,
        description="SSG engine this theme is designed for"
    )
    
    # Installation configuration
    installation_method: ThemeInstallMethod = Field(
        ...,
        description="Method used to install and configure this theme"
    )
    
    source: str = Field(
        ...,
        description="Theme source location (GitHub repo, npm package, etc.)",
        min_length=3
    )
    
    # Dependencies and requirements
    required_plugins: List[str] = Field(
        default_factory=list,
        description="List of required plugins/dependencies for this theme"
    )
    
    minimum_engine_version: Optional[str] = Field(
        None,
        description="Minimum SSG engine version required (e.g., '4.0.0')"
    )
    
    # Hosting compatibility
    github_pages_compatible: bool = Field(
        default=False,
        description="Whether this theme works with GitHub Pages hosting"
    )
    
    # Documentation and preview
    repo_url: Optional[str] = Field(
        None,
        description="GitHub repository URL for theme source code",
        pattern=r"^https://github\.com/[^/]+/[^/]+/?$"
    )
    
    demo_url: Optional[str] = Field(
        None,
        description="Live demo URL showcasing the theme",
    )
    
    documentation_url: Optional[str] = Field(
        None,
        description="Theme-specific documentation URL"
    )
    
    # Business and categorization
    categories: List[str] = Field(
        default_factory=list,
        description="Business categories this theme serves (business, blog, portfolio, etc.)"
    )
    
    tags: List[str] = Field(
        default_factory=list,
        description="Searchable tags for theme discovery"
    )
    
    # Theme customization
    customization_options: Dict[str, Any] = Field(
        default_factory=dict,
        description="Available customization options (colors, layouts, features, etc.)"
    )
    
    # Quality and maintenance
    verified: bool = Field(
        default=False,
        description="Whether this theme has been tested and verified by our team"
    )
    
    maintenance_status: Literal["active", "stable", "deprecated"] = Field(
        default="active",
        description="Theme maintenance status"
    )
    
    # Business information  
    license_type: Optional[str] = Field(
        None,
        description="Theme license (MIT, GPL, Commercial, etc.)"
    )
    
    author_name: Optional[str] = Field(
        None,
        description="Theme author or organization name"
    )
    
    # Installation-specific metadata
    installation_config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Engine-specific installation configuration"
    )
    
    @field_validator('categories')
    @classmethod
    def validate_categories(cls, v):
        """Ensure categories use standard business terms"""
        standard_categories = {
            'business', 'professional', 'corporate', 'startup',
            'blog', 'personal', 'portfolio', 'creative',
            'ecommerce', 'store', 'shop', 'retail',
            'nonprofit', 'charity', 'community', 'organization',
            'documentation', 'technical', 'developer', 'api',
            'restaurant', 'food', 'hospitality', 'service',
            'law', 'legal', 'medical', 'healthcare',
            'real_estate', 'property', 'construction',
            'education', 'school', 'university', 'training'
        }
        
        for category in v:
            if category.lower() not in standard_categories:
                # Allow the category but could warn in logs
                pass
                
        return v
    
    @field_validator('source')
    @classmethod
    def validate_source_format(cls, v, info):
        """Validate source format based on installation method"""
        if 'installation_method' in info.data:
            method = info.data['installation_method']
            
            # Validate source format for different installation methods
            if method == ThemeInstallMethod.REMOTE_THEME:
                # Should be in format: owner/repo@version or owner/repo
                if not ('/' in v and len(v.split('/')) >= 2):
                    raise ValueError(f"Remote theme source must be in 'owner/repo' format, got: {v}")
            
            elif method == ThemeInstallMethod.NPM_PACKAGE:
                # Should be npm package name (could start with @)
                if not (v.startswith('@') or '/' not in v):
                    # Allow both @scope/package and package-name formats
                    pass
            
            elif method in [ThemeInstallMethod.GIT_CLONE, ThemeInstallMethod.TEMPLATE_REPO]:
                # Should be full git URL
                if not (v.startswith('https://') or v.startswith('git@')):
                    raise ValueError(f"Git source must be full URL, got: {v}")
        
        return v
    
    def get_installation_commands(self) -> List[str]:
        """
        Generate installation commands based on theme configuration.
        
        Returns:
            List of shell commands to install this theme
        """
        commands = []
        
        if self.installation_method == ThemeInstallMethod.REMOTE_THEME:
            # Jekyll remote theme setup
            commands.extend([
                f"echo 'remote_theme: {self.source}' >> _config.yml"
            ])
            
        elif self.installation_method == ThemeInstallMethod.GIT_CLONE:
            # Clone and copy theme files
            repo_name = self.source.split('/')[-1].replace('.git', '')
            commands.extend([
                f"git clone {self.source} {repo_name}",
                f"cp -r {repo_name}/_layouts/* _layouts/ 2>/dev/null || true",
                f"cp -r {repo_name}/_sass/* _sass/ 2>/dev/null || true", 
                f"cp -r {repo_name}/_includes/* _includes/ 2>/dev/null || true",
                f"rm -rf {repo_name}"
            ])
            
        elif self.installation_method == ThemeInstallMethod.NPM_PACKAGE:
            # NPM package installation
            commands.extend([
                f"npm install {self.source}"
            ])
            
        elif self.installation_method == ThemeInstallMethod.GIT_SUBMODULE:
            # Hugo git submodule
            theme_name = self.source.split('/')[-1].replace('.git', '')
            commands.extend([
                f"git submodule add {self.source} themes/{theme_name}",
                f"echo 'theme = \"{theme_name}\"' >> config.toml"
            ])
        
        # Add plugin installation commands
        if self.required_plugins:
            if self.engine == "jekyll":
                plugins_str = " ".join(self.required_plugins)
                commands.append(f"echo 'plugins: [{', '.join(self.required_plugins)}]' >> _config.yml")
            elif self.engine in ["astro", "gatsby", "nextjs"]:
                plugins_str = " ".join(self.required_plugins)
                commands.append(f"npm install {plugins_str}")
        
        return commands
    
    def get_customization_env_vars(self, theme_config: Dict[str, Any]) -> Dict[str, str]:
        """
        Convert theme customization config to environment variables.
        
        Args:
            theme_config: Client-specific theme customization
            
        Returns:
            Dictionary of environment variables for CodeBuild
        """
        env_vars = {}
        
        # Add theme-specific environment variables
        env_vars[f"THEME_ID"] = self.id
        env_vars[f"THEME_ENGINE"] = self.engine
        env_vars[f"THEME_INSTALLATION_METHOD"] = self.installation_method
        
        # Convert customization options to env vars
        for key, value in theme_config.items():
            env_key = f"THEME_{key.upper()}"
            env_vars[env_key] = str(value)
        
        # Add engine-specific theme configurations
        if self.engine == "jekyll":
            if "skin" in theme_config:
                env_vars["JEKYLL_THEME_SKIN"] = theme_config["skin"]
            if "author_name" in theme_config:
                env_vars["JEKYLL_AUTHOR_NAME"] = theme_config["author_name"]
                
        return env_vars
    
    def is_compatible_with_hosting(self, hosting_pattern: str) -> bool:
        """
        Check if theme is compatible with specified hosting pattern.
        
        Args:
            hosting_pattern: Hosting pattern (aws, github, hybrid, aws_minimal)
            
        Returns:
            True if compatible, False otherwise
        """
        if hosting_pattern == "github" or hosting_pattern == "hybrid":
            return self.github_pages_compatible
        
        # AWS hosting patterns support all themes
        return True