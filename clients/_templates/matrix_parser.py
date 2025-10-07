"""
Tech Stack Product Matrix Parser

Reads pricing, AWS services, and suitability data from tech-stack-product-matrix.md
to drive client configuration validation and recommendations.

This replaces hardcoded data structures with dynamic matrix-driven configuration.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class SuitabilityRating(str, Enum):
    """Suitability ratings from the matrix"""
    EXCELLENT = "excellent"
    GOOD = "good"
    LIMITED = "limited"
    NOT_SUITABLE = "not_suitable"


@dataclass
class StackInfo:
    """Information about a technology stack from the matrix"""
    name: str
    framework: str
    setup_cost_range: Tuple[int, int]
    monthly_cost_range: Tuple[int, int]
    target_markets: List[str]
    aws_services: List[str]
    suitability_by_use_case: Dict[str, SuitabilityRating]


@dataclass
class CMSInfo:
    """CMS comparison information"""
    name: str
    type: str
    monthly_cost: str
    client_experience: str
    best_for: str
    setup_complexity: str


class TechStackMatrix:
    """
    Parser for tech-stack-product-matrix.md that provides dynamic access
    to pricing, AWS services, and validation rules.
    """

    def __init__(self, matrix_file: Optional[str] = None):
        if matrix_file is None:
            # Default to matrix file in documents directory
            current_dir = Path(__file__).parent
            matrix_file = str(current_dir.parent.parent.parent / "documents" / "tech-stack-product-matrix.md")

        self.matrix_file = Path(matrix_file)
        self._stacks: Dict[str, StackInfo] = {}
        self._cms_info: Dict[str, CMSInfo] = {}
        self._migration_pathways: Dict[str, List[str]] = {}

        if self.matrix_file.exists():
            self._parse_matrix()
        else:
            raise FileNotFoundError(f"Matrix file not found: {matrix_file}")

    def _parse_matrix(self):
        """Parse the markdown matrix file"""
        content = self.matrix_file.read_text()

        # Parse the main matrix table
        self._parse_main_matrix(content)

        # Parse AWS services table
        self._parse_aws_services(content)

        # Parse CMS comparison
        self._parse_cms_info(content)

        # Parse migration pathways
        self._parse_migration_pathways(content)

    def _parse_main_matrix(self, content: str):
        """Parse the main tech stack vs product offering matrix"""
        # Find the main matrix table
        matrix_start = content.find("| Tech Stack | Framework |")
        if matrix_start == -1:
            return

        # Extract table rows
        lines = content[matrix_start:].split('\n')
        header_line = lines[0]

        # Skip header and separator lines
        data_lines = [line for line in lines[2:] if line.strip().startswith('|') and '**' in line]

        for line in data_lines:
            if not line.strip():
                continue

            self._parse_matrix_row(line)

    def _parse_matrix_row(self, line: str):
        """Parse a single row from the matrix table"""
        cells = [cell.strip() for cell in line.split('|')[1:-1]]  # Remove empty first/last

        if len(cells) < 9:
            return

        tech_stack = cells[0].replace('**', '').strip()
        framework = cells[1].strip()

        # Parse pricing and suitability from each use case column
        use_cases = [
            "personal_portfolio", "small_business_sites", "simple_ecommerce",
            "content_blog_sites", "medium_ecommerce", "enterprise_ecommerce",
            "custom_applications", "legacy_migrations"
        ]

        suitability_by_use_case = {}
        setup_costs = []
        monthly_costs = []
        target_markets = set()

        for i, use_case in enumerate(use_cases):
            if i + 2 >= len(cells):
                continue

            cell_content = cells[i + 2]

            # Extract suitability rating
            if "✓ **Excellent**" in cell_content:
                suitability_by_use_case[use_case] = SuitabilityRating.EXCELLENT
            elif "○ **Good**" in cell_content:
                suitability_by_use_case[use_case] = SuitabilityRating.GOOD
            elif "△ **Limited**" in cell_content:
                suitability_by_use_case[use_case] = SuitabilityRating.LIMITED
            elif "✗ **Not Suitable**" in cell_content:
                suitability_by_use_case[use_case] = SuitabilityRating.NOT_SUITABLE

            # Extract pricing - handle different formats including HTML <br/> tags
            # Pattern: $480-1,440 | $25-50 or $480-1,440 \| $25-50
            pricing_match = re.search(r'\$([0-9,]+)-([0-9,]+)\s*[\|\\\\]\s*\$([0-9,]+)-([0-9,]+)', cell_content)
            if pricing_match:
                setup_min = int(pricing_match.group(1).replace(',', ''))
                setup_max = int(pricing_match.group(2).replace(',', ''))
                monthly_min = int(pricing_match.group(3).replace(',', ''))
                monthly_max = int(pricing_match.group(4).replace(',', ''))

                setup_costs.extend([setup_min, setup_max])
                monthly_costs.extend([monthly_min, monthly_max])

            # Extract target markets
            if "Target: I" in cell_content:
                target_markets.add("individual")
            if "Target: S" in cell_content:
                target_markets.add("small_business")
            if "Target: E" in cell_content:
                target_markets.add("enterprise")

        # Calculate overall cost ranges
        setup_cost_range = (min(setup_costs), max(setup_costs)) if setup_costs else (0, 0)
        monthly_cost_range = (min(monthly_costs), max(monthly_costs)) if monthly_costs else (0, 0)

        # Convert tech stack name to snake_case identifier
        stack_id = self._normalize_stack_name(tech_stack)

        self._stacks[stack_id] = StackInfo(
            name=tech_stack,
            framework=framework,
            setup_cost_range=setup_cost_range,
            monthly_cost_range=monthly_cost_range,
            target_markets=list(target_markets),
            aws_services=[],  # Will be populated by _parse_aws_services
            suitability_by_use_case=suitability_by_use_case
        )

    def _parse_aws_services(self, content: str):
        """Parse AWS services by tech stack table"""
        services_start = content.find("| Tech Stack | Framework Knowledge | Primary AWS Services |")
        if services_start == -1:
            return

        lines = content[services_start:].split('\n')

        # Skip header and separator lines
        data_lines = [line for line in lines[2:] if line.strip().startswith('|') and '**' in line]

        for line in data_lines:
            if not line.strip():
                continue

            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            if len(cells) < 4:
                continue

            tech_stack = cells[0].replace('**', '').strip()
            primary_services = [s.strip() for s in cells[2].split(',')]
            secondary_services = [s.strip() for s in cells[3].split(',')]

            stack_id = self._normalize_stack_name(tech_stack)

            if stack_id in self._stacks:
                self._stacks[stack_id].aws_services = primary_services + secondary_services

    def _parse_cms_info(self, content: str):
        """Parse CMS comparison information"""
        cms_start = content.find("| CMS Solution | Type | Monthly Cost | Client Experience |")
        if cms_start == -1:
            return

        lines = content[cms_start:].split('\n')
        data_lines = [line for line in lines[2:] if line.strip().startswith('|') and '**' in line]

        for line in data_lines:
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            if len(cells) < 6:
                continue

            cms_name = cells[0].replace('**', '').strip()

            self._cms_info[cms_name.lower()] = CMSInfo(
                name=cms_name,
                type=cells[1],
                monthly_cost=cells[2],
                client_experience=cells[3],
                best_for=cells[4],
                setup_complexity=cells[5]
            )

    def _parse_migration_pathways(self, content: str):
        """Parse migration pathway recommendations"""
        migration_start = content.find("| Current Platform | Recommended Target Stacks |")
        if migration_start == -1:
            return

        lines = content[migration_start:].split('\n')
        data_lines = [line for line in lines[2:] if line.strip().startswith('|') and '**' in line]

        for line in data_lines:
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            if len(cells) < 2:
                continue

            current_platform = cells[0].replace('**', '').strip()
            target_stacks = [s.strip() for s in cells[1].split(',')]

            self._migration_pathways[current_platform.lower()] = target_stacks

    def _normalize_stack_name(self, name: str) -> str:
        """Convert tech stack name to normalized identifier"""
        # Remove markdown formatting
        name = re.sub(r'\*\*', '', name)

        # Convert to snake_case
        name = re.sub(r'[^a-zA-Z0-9]+', '_', name.lower())
        name = re.sub(r'^_+|_+$', '', name)  # Remove leading/trailing underscores

        # Map common variations
        mappings = {
            'static_html_css_js': 'static_marketing',
            'static_decap_cms': 'static_decap_cms',
            'static_tina_cms': 'static_tina_cms',
            'static_sanity': 'static_sanity',
            'static_contentful': 'static_contentful',
            'static_snipcart': 'static_snipcart',
            'static_foxy_io': 'static_foxy',
            'wordpress_woocommerce_lightsail': 'wordpress_lightsail',
            'aws_amplify': 'amplify_ecommerce',
            'fastapi_pydantic_api': 'fastapi_pydantic_api',
            'fastapi_react_vue': 'fastapi_react_vue',
            'aws_serverless': 'serverless_applications',

            # NEW: Astro variants (Tier 1 vs Tier 2)
            'astro_headless_cms': 'astro_template_basic',  # Default to basic variant
            'astro_basic_headless_cms': 'astro_template_basic',
            'astro_template_basic': 'astro_template_basic',
            'astro_advanced_cms': 'astro_advanced_cms',

            # NEW: WordPress ECS variants (Tier 2 vs Tier 3)
            'wordpress_ecs': 'wordpress_ecs_professional',  # Default to professional
            'wordpress_woocommerce_ecs': 'wordpress_ecs_professional',
            'wordpress_ecs_professional': 'wordpress_ecs_professional',
            'wordpress_ecs_enterprise': 'wordpress_ecs_enterprise',

            # NEW: Next.js/Nuxt.js variants (Tier 2 vs Tier 3)
            'next_js_headless_cms': 'nextjs_professional_headless_cms',
            'nextjs_headless_cms': 'nextjs_professional_headless_cms',  # Default to professional
            'nextjs_professional_headless_cms': 'nextjs_professional_headless_cms',
            'nextjs_enterprise_applications': 'nextjs_enterprise_applications',
            'nuxt_js_headless_cms': 'nuxtjs_professional_headless_cms',
            'nuxtjs_headless_cms': 'nuxtjs_professional_headless_cms',
            'nuxtjs_professional_headless_cms': 'nuxtjs_professional_headless_cms',
            'nuxtjs_enterprise_applications': 'nuxtjs_enterprise_applications',

            # NEW: Shopify variants consolidation
            'shopify_standard': 'shopify_standard_dns',
            'shopify_aws_integrations': 'shopify_aws_basic_integration',
            'shopify_aws_integrated': 'shopify_aws_basic_integration',
            'shopify_customizations': 'shopify_aws_basic_integration',
            'shopify_standard_dns': 'shopify_standard_dns',
            'shopify_aws_basic_integration': 'shopify_aws_basic_integration',
            'shopify_aws_advanced_integration': 'shopify_aws_advanced_integration',
            'headless_shopify_gatsby': 'headless_shopify_custom_frontend',
            'headless_shopify_next_js': 'headless_shopify_custom_frontend',
            'headless_shopify_nextjs': 'headless_shopify_custom_frontend',
            'headless_shopify_custom_frontend': 'headless_shopify_custom_frontend',

            # Framework variants
            'gatsby_headless_cms': 'gatsby_headless_cms',

            # Legacy mappings
            'static_portfolio': 'static_marketing',  # Portfolio is a variant of static marketing
            'custom_applications': 'fastapi_react_vue'  # Custom apps typically use full-stack frameworks
        }

        return mappings.get(name, name)

    # Public API methods

    def get_stack_info(self, stack_type: str) -> Optional[StackInfo]:
        """Get complete information about a technology stack"""
        # Direct lookup first
        if stack_type in self._stacks:
            return self._stacks[stack_type]

        # Fallback for variant stacks not yet in matrix
        fallback_mappings = {
            'astro_template_basic': 'astro_headless_cms',
            'astro_advanced_cms': 'astro_headless_cms',
            'wordpress_ecs_professional': 'wordpress_ecs',
            'wordpress_ecs_enterprise': 'wordpress_ecs',
            'nextjs_professional_headless_cms': 'nextjs_headless_cms',
            'nextjs_enterprise_applications': 'nextjs_headless_cms',
            'nuxtjs_professional_headless_cms': 'nuxtjs_headless_cms',
            'nuxtjs_enterprise_applications': 'nuxtjs_headless_cms',
            'shopify_standard_dns': 'shopify_standard',
            'shopify_aws_basic_integration': 'shopify_aws_integrated',
            'shopify_aws_advanced_integration': 'shopify_aws_integrated',
            'headless_shopify_custom_frontend': 'headless_shopify_nextjs'
        }

        fallback = fallback_mappings.get(stack_type)
        if fallback and fallback in self._stacks:
            return self._stacks[fallback]

        return None

    def get_pricing_range(self, stack_type: str) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """Get (setup_cost_range, monthly_cost_range) for a stack"""
        stack = self._stacks.get(stack_type)
        if stack:
            return (stack.setup_cost_range, stack.monthly_cost_range)
        return None

    def get_aws_services(self, stack_type: str) -> List[str]:
        """Get required AWS services for a stack"""
        stack = self._stacks.get(stack_type)
        return stack.aws_services if stack else []

    def is_suitable_for_market(self, stack_type: str, target_market: str) -> bool:
        """Check if a stack is suitable for a target market"""
        stack = self._stacks.get(stack_type)
        if not stack:
            return False

        return target_market in stack.target_markets

    def get_recommended_stacks(self, target_market: str, use_case: Optional[str] = None) -> List[str]:
        """Get recommended stacks for a target market and optional use case"""
        recommendations = []

        for stack_id, stack in self._stacks.items():
            if target_market not in stack.target_markets:
                continue

            if use_case:
                # Check suitability for specific use case
                suitability = stack.suitability_by_use_case.get(use_case)
                if suitability in [SuitabilityRating.EXCELLENT, SuitabilityRating.GOOD]:
                    recommendations.append(stack_id)
            else:
                recommendations.append(stack_id)

        return recommendations

    def validate_pricing(self, stack_type: str, setup_cost: int, monthly_fee: int) -> bool:
        """Validate if pricing is within reasonable range for stack"""
        pricing = self.get_pricing_range(stack_type)
        if not pricing:
            return True  # Allow if no pricing data

        setup_range, monthly_range = pricing

        # Allow 50% flexibility above max for custom pricing
        setup_valid = setup_range[0] <= setup_cost <= setup_range[1] * 1.5
        monthly_valid = monthly_range[0] <= monthly_fee <= monthly_range[1] * 1.5

        return setup_valid and monthly_valid

    def get_all_stacks(self) -> List[str]:
        """Get list of all available stack types"""
        return list(self._stacks.keys())

    def get_cms_info(self, cms_name: str) -> Optional[CMSInfo]:
        """Get information about a CMS solution"""
        return self._cms_info.get(cms_name.lower())

    def get_migration_recommendations(self, current_platform: str) -> List[str]:
        """Get recommended migration targets for a current platform"""
        return self._migration_pathways.get(current_platform.lower(), [])


# Global instance for easy access
_matrix_instance: Optional[TechStackMatrix] = None

def get_matrix() -> TechStackMatrix:
    """Get the global matrix instance"""
    global _matrix_instance
    if _matrix_instance is None:
        _matrix_instance = TechStackMatrix()
    return _matrix_instance


def migrate_stack_type(old_stack_type: str) -> str:
    """
    Migrate old stack types to new variant naming.

    Use this to update existing client configurations when stack names change.

    Args:
        old_stack_type: The old stack type name

    Returns:
        str: The new stack type name (or original if no migration needed)

    Example:
        # Update existing client config
        old_config = ClientConfig.from_dict(json.load(open('client.json')))
        new_stack_type = migrate_stack_type(old_config.stack_type)
        if new_stack_type != old_config.stack_type:
            old_config.stack_type = new_stack_type
            json.dump(old_config.to_dict(), open('client.json', 'w'))
    """
    migrations = {
        # Default ambiguous names to most common tier variant
        'astro_headless_cms': 'astro_template_basic',  # Default to basic variant (Tier 1)
        'wordpress_ecs': 'wordpress_ecs_professional',  # Default to professional (Tier 2)
        'nextjs_headless_cms': 'nextjs_professional_headless_cms',  # Default to professional (Tier 2)
        'nuxtjs_headless_cms': 'nuxtjs_professional_headless_cms',  # Default to professional (Tier 2)
        'shopify_aws_integrated': 'shopify_aws_basic_integration',  # Default to basic integration (Tier 2)
        'headless_shopify_nextjs': 'headless_shopify_custom_frontend',  # Update to consolidated name (Tier 3)
        'headless_shopify_gatsby': 'headless_shopify_custom_frontend',  # Update to consolidated name (Tier 3)
        'shopify_customizations': 'shopify_aws_basic_integration',  # Old name -> new name
        'shopify_aws_integrations': 'shopify_aws_basic_integration'  # Old name -> new name
    }

    return migrations.get(old_stack_type, old_stack_type)