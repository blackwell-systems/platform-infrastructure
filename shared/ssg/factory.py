"""
SSG Engine Factory

Provides the factory pattern for creating SSG engine configurations.
Centralizes engine instantiation and template discovery across all engines.
"""

from typing import Dict, List, Any, Literal

from .core_models import SSGEngineType, ECommerceProvider, SSGTemplate
from .base_engine import SSGEngineConfig


class SSGEngineFactory:
    """Factory for creating SSG engine configurations"""

    _engines = {
        "eleventy": None,  # Will be populated when engines/ modules are created
        "hugo": None,
        "astro": None,
        "jekyll": None,
        "nextjs": None,
        "nuxt": None,
        "gatsby": None,
    }

    @classmethod
    def create_engine(
        cls, engine_type: SSGEngineType, template_variant: str = "default"
    ) -> SSGEngineConfig:
        """Create an SSG engine configuration"""
        if engine_type not in cls._engines:
            raise ValueError(f"Unsupported SSG engine: {engine_type}")

        # Import engines dynamically to avoid circular imports
        from .engines import (
            EleventyConfig, HugoConfig, AstroConfig, JekyllConfig,
            NextJSConfig, NuxtConfig, GatsbyConfig
        )
        
        engine_classes = {
            "eleventy": EleventyConfig,
            "hugo": HugoConfig,
            "astro": AstroConfig,
            "jekyll": JekyllConfig,
            "nextjs": NextJSConfig,
            "nuxt": NuxtConfig,
            "gatsby": GatsbyConfig,
        }

        engine_class = engine_classes.get(engine_type)
        if not engine_class:
            raise ValueError(f"Engine class not found for: {engine_type}")

        return engine_class(template_variant)

    @classmethod
    def get_available_engines(cls) -> List[str]:
        """Get list of available SSG engines"""
        return list(cls._engines.keys())

    @classmethod
    def get_engine_templates(cls, engine_type: SSGEngineType) -> List[SSGTemplate]:
        """Get available templates for an engine"""
        engine = cls.create_engine(engine_type)
        return engine.available_templates
    
    @classmethod
    def get_ecommerce_templates(cls) -> Dict[str, List[SSGTemplate]]:
        """Get all e-commerce templates across all engines"""
        ecommerce_templates = {}
        
        for engine_type in cls._engines.keys():
            engine = cls.create_engine(engine_type)
            templates = [t for t in engine.available_templates if t.supports_ecommerce]
            if templates:
                ecommerce_templates[engine_type] = templates
                
        return ecommerce_templates
    
    @classmethod
    def get_templates_by_provider(cls, provider: ECommerceProvider) -> Dict[str, List[SSGTemplate]]:
        """Get templates that support a specific e-commerce provider"""
        provider_templates = {}
        
        for engine_type in cls._engines.keys():
            engine = cls.create_engine(engine_type)
            templates = [
                t for t in engine.available_templates 
                if (t.supports_ecommerce and 
                    t.ecommerce_integration and 
                    t.ecommerce_integration.provider == provider)
            ]
            if templates:
                provider_templates[engine_type] = templates
                
        return provider_templates
    
    @classmethod
    def get_recommended_stack_for_ecommerce(
        cls, 
        provider: ECommerceProvider, 
        complexity: Literal["simple", "advanced", "enterprise"] = "simple"
    ) -> List[Dict[str, Any]]:
        """Get recommended SSG engine and template combinations for e-commerce"""
        recommendations = []
        
        complexity_mapping = {
            "simple": "low",
            "advanced": "high", 
            "enterprise": "high"  # Map enterprise to high for now
        }
        
        target_complexity = complexity_mapping.get(complexity, "low")
        provider_templates = cls.get_templates_by_provider(provider)
        
        for engine_type, templates in provider_templates.items():
            for template in templates:
                if (template.ecommerce_integration and 
                    template.ecommerce_integration.setup_complexity == target_complexity):
                    recommendations.append({
                        "engine": engine_type,
                        "template": template.name,
                        "provider": provider,
                        "complexity": complexity,
                        "estimated_hours": template.estimated_setup_hours,
                        "monthly_cost_range": template.ecommerce_integration.monthly_cost_range
                    })
        
        return sorted(recommendations, key=lambda x: x["estimated_hours"])