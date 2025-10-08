# CMS/SSG Flexibility Refactoring Plan
## From Hardcoded Pairings to Client-Configurable Architecture

**Status**: Planning Phase
**Priority**: High - Addresses arbitrary limitations in current stack matrix
**Impact**: Increases client choice and revenue potential while reducing code duplication
**Timeline**: 5 weeks

---

## 🚨 **Problem Statement**

### Current Architecture Limitations
Our current stack implementation artificially constrains SSG/CMS combinations:

```python
# ❌ Current: Hardcoded, inflexible pairings
class StaticDecapCMSStack(BaseSSGStack):  # Forces Eleventy only
class AstroTinaCMSStack(BaseSSGStack):    # Forces Astro only
class GatsbyContentfulStack(BaseSSGStack): # Forces Gatsby only
```

**Business Impact:**
- **Reduced Client Choice**: Clients must accept arbitrary SSG/CMS pairings
- **Revenue Limitations**: Single CMS tier cannot serve different technical comfort levels
- **Code Duplication**: Need separate stack classes for every SSG/CMS combination
- **Maintenance Overhead**: 20+ stack classes instead of flexible architecture

### **Strategic Question Raised**
> *"Why Static + Decap CMS → Only Eleventy? Why not Astro + Decap or Hugo + Decap?"*

**Answer**: There's no technical reason for these constraints. It's an architectural limitation that reduces business flexibility.

---

## 🎯 **Solution Architecture**

### **New Flexible Design**
```python
# ✅ New: CMS-focused with SSG flexibility
class DecapCMSStack(BaseCMSStack):        # Accepts: eleventy, astro, hugo, gatsby
class TinaCMSStack(BaseCMSStack):         # Accepts: astro, nextjs, nuxt, eleventy
class SanityCMSStack(BaseCMSStack):       # Accepts: astro, gatsby, nextjs, nuxt
class ContentfulStack(BaseCMSStack):      # Accepts: gatsby, astro, nextjs, nuxt
```

### **Client Benefits**
- **Choice Within CMS Tier**: Select SSG based on technical comfort and requirements
- **Better Value Alignment**: Same monthly cost ($50-85) but different complexity levels
- **Future Flexibility**: Easy to add new SSG engines to existing CMS tiers

---

## 📊 **SSG/CMS Compatibility Matrix**

### **Decap CMS Stack** (Self-Managed • $50-75/month)
| SSG Engine | Setup Cost | Technical Level | Best For |
|------------|------------|-----------------|----------|
| **Hugo + Decap** | $960-1,800 | Technical | Large content sites, documentation, maximum performance |
| **Eleventy + Decap** | $1,200-2,160 | Intermediate | Business sites, blogs, balanced complexity |
| **Astro + Decap** | $1,440-2,400 | Intermediate-Advanced | Modern interactive sites, component islands |
| **Gatsby + Decap** | $1,800-2,640 | Advanced | Content-heavy sites, GraphQL integration |

### **Tina CMS Stack** (Self-Managed • $60-85/month)
| SSG Engine | Setup Cost | Technical Level | Best For |
|------------|------------|-----------------|----------|
| **Astro + Tina** | $1,200-2,400 | Intermediate | Component islands, visual editing balance |
| **Next.js + Tina** | $1,800-3,600 | Advanced | React ecosystem, full-stack capabilities |
| **Nuxt + Tina** | $1,800-3,600 | Advanced | Vue ecosystem, server-side rendering |
| **Eleventy + Tina** | $1,440-2,640 | Intermediate | Simple builds with visual editing |

### **Sanity CMS Stack** (Self-Managed • $65-90/month)
| SSG Engine | Setup Cost | Technical Level | Best For |
|------------|------------|-----------------|----------|
| **Astro + Sanity** | $1,800-3,000 | Intermediate-Advanced | Structured content, component flexibility |
| **Gatsby + Sanity** | $2,400-3,600 | Advanced | Content sites, GraphQL + Sanity integration |
| **Next.js + Sanity** | $2,400-4,200 | Advanced | React ecosystem, complex data modeling |
| **Nuxt + Sanity** | $2,400-4,200 | Advanced | Vue ecosystem, structured content |

### **Contentful Stack** (Self-Managed • $75-125/month)
| SSG Engine | Setup Cost | Technical Level | Best For |
|------------|------------|-----------------|----------|
| **Gatsby + Contentful** | $2,400-4,200 | Advanced | Enterprise content sites, GraphQL |
| **Astro + Contentful** | $2,100-3,600 | Intermediate-Advanced | Performance + enterprise CMS |
| **Next.js + Contentful** | $3,000-4,800 | Advanced | React + enterprise features |
| **Nuxt + Contentful** | $3,000-4,800 | Advanced | Vue + enterprise content management |

---

## 🏗️ **Technical Implementation Plan**

### **Phase 1: Architecture Foundation (Week 1)**

#### 1.1 Create Base CMS Stack Class
**File**: `stacks/shared/base_cms_stack.py`

```python
class BaseCMSStack(BaseSSGStack):
    """
    Base class for CMS-enabled stacks with flexible SSG engine support.
    """

    # Compatibility matrix - which SSG engines work with each CMS
    COMPATIBLE_SSG_ENGINES: Dict[str, List[str]] = {
        "decap": ["eleventy", "astro", "hugo", "gatsby"],
        "tina": ["astro", "nextjs", "nuxt", "eleventy"],
        "sanity": ["astro", "gatsby", "nextjs", "nuxt"],
        "contentful": ["gatsby", "astro", "nextjs", "nuxt"]
    }

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        client_id: str,
        domain: str,
        cms_provider: str,
        ssg_engine: str = "eleventy",  # Default but configurable
        **kwargs
    ):
        # Validate compatibility
        self._validate_ssg_cms_compatibility(ssg_engine, cms_provider)

        # Resolve template variant for (SSG, CMS) combination
        template_variant = self._resolve_template_variant(ssg_engine, cms_provider)

        # Create flexible SSG configuration
        ssg_config = StaticSiteConfig(
            client_id=client_id,
            domain=domain,
            ssg_engine=ssg_engine,     # Client choice
            template_variant=template_variant,
            cms_provider=cms_provider,
            performance_tier="optimized"
        )

        super().__init__(scope, construct_id, ssg_config, **kwargs)
        self._setup_cms_integration()  # CMS-specific setup
```

#### 1.2 Template Variant Resolution System
**Logic**: Map (SSG Engine, CMS Provider) → Template Variant

```python
def _resolve_template_variant(self, ssg_engine: str, cms_provider: str) -> str:
    """Map SSG + CMS combination to appropriate template variant"""
    template_mapping = {
        # Decap CMS variants
        ("eleventy", "decap"): "decap_cms_business",
        ("astro", "decap"): "decap_cms_interactive",
        ("hugo", "decap"): "decap_cms_performance",
        ("gatsby", "decap"): "decap_cms_content",

        # Tina CMS variants
        ("astro", "tina"): "tina_cms_visual",
        ("nextjs", "tina"): "tina_cms_react",
        ("nuxt", "tina"): "tina_cms_vue",
        ("eleventy", "tina"): "tina_cms_simple",

        # Sanity variants
        ("astro", "sanity"): "sanity_cms_structured",
        ("gatsby", "sanity"): "sanity_cms_graphql",
        ("nextjs", "sanity"): "sanity_cms_react",
        ("nuxt", "sanity"): "sanity_cms_vue",

        # Contentful variants
        ("gatsby", "contentful"): "contentful_cms_enterprise",
        ("astro", "contentful"): "contentful_cms_performance",
        ("nextjs", "contentful"): "contentful_cms_react",
        ("nuxt", "contentful"): "contentful_cms_vue"
    }

    variant = template_mapping.get((ssg_engine, cms_provider))
    if not variant:
        # Fallback to generic CMS template
        variant = f"{cms_provider}_cms_generic"

    return variant
```

### **Phase 2: Concrete CMS Stack Implementation (Week 2)**

#### 2.1 Decap CMS Stack
**File**: `stacks/cms/decap_cms_stack.py`

```python
class DecapCMSStack(BaseCMSStack):
    """
    Decap CMS stack supporting multiple SSG engines.

    Compatible SSG Engines: Eleventy, Astro, Hugo, Gatsby
    Management Model: Self-managed content editing
    Monthly Cost: $50-75 (hosting + CMS free)
    Setup Cost: $960-2,640 (varies by SSG complexity)
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        client_id: str,
        domain: str,
        ssg_engine: str = "eleventy",  # Client configurable
        enable_identity: bool = True,
        **kwargs
    ):
        super().__init__(
            scope, construct_id, client_id, domain,
            cms_provider="decap",
            ssg_engine=ssg_engine,  # Pass through client choice
            **kwargs
        )
        self.enable_identity = enable_identity

    def _setup_cms_integration(self):
        """Set up Decap CMS specific infrastructure"""
        # Base Decap configuration
        decap_vars = {
            "CMS_PROVIDER": "decap",
            "DECAP_CMS_ENABLED": "true",
            "CMS_CONFIG_PATH": "admin/config.yml",
            "CMS_ADMIN_PATH": "/admin",
            "CMS_BACKEND": "git-gateway",
            "CMS_MEDIA_FOLDER": self._get_media_folder(),
            "CMS_PUBLIC_FOLDER": self._get_public_folder()
        }

        # SSG-specific Decap configuration
        ssg_specific_vars = self._get_ssg_specific_decap_config()
        decap_vars.update(ssg_specific_vars)

        self.add_environment_variables(decap_vars)

        # Add form handler if needed for static SSGs
        if self.ssg_config.ssg_engine in ["eleventy", "hugo"]:
            self._setup_form_handler()

    def _get_ssg_specific_decap_config(self) -> Dict[str, str]:
        """Get SSG-specific Decap CMS configuration"""
        ssg_configs = {
            "eleventy": {
                "DECAP_COLLECTIONS_PATH": "src/_data",
                "DECAP_POSTS_PATH": "src/posts",
                "ELEVENTY_DECAP_INTEGRATION": "true"
            },
            "astro": {
                "DECAP_COLLECTIONS_PATH": "src/content",
                "DECAP_POSTS_PATH": "src/content/blog",
                "ASTRO_DECAP_INTEGRATION": "true",
                "ASTRO_CONTENT_COLLECTIONS": "true"
            },
            "hugo": {
                "DECAP_COLLECTIONS_PATH": "content",
                "DECAP_POSTS_PATH": "content/posts",
                "HUGO_DECAP_INTEGRATION": "true"
            },
            "gatsby": {
                "DECAP_COLLECTIONS_PATH": "content",
                "DECAP_POSTS_PATH": "content/blog",
                "GATSBY_DECAP_INTEGRATION": "true"
            }
        }

        return ssg_configs.get(self.ssg_config.ssg_engine, {})

    def get_cms_setup_guide(self) -> Dict[str, Any]:
        """Get setup guide specific to chosen SSG engine"""
        guides = {
            "eleventy": {
                "title": "Eleventy + Decap CMS Setup",
                "complexity": "Intermediate",
                "setup_time": "2-3 hours",
                "steps": [
                    "Configure Eleventy collections for CMS content",
                    "Set up admin/config.yml with Eleventy paths",
                    "Enable Netlify Identity for authentication",
                    "Deploy and test content editing workflow"
                ],
                "template_features": [
                    "Fast builds (< 10 seconds)",
                    "Simple templating with Liquid/Nunjucks",
                    "Markdown-based content",
                    "Git-based workflow"
                ],
                "best_for": "Business websites, blogs, simple content sites"
            },
            "astro": {
                "title": "Astro + Decap CMS Setup",
                "complexity": "Intermediate-Advanced",
                "setup_time": "3-4 hours",
                "steps": [
                    "Configure Astro content collections",
                    "Set up Decap CMS with Astro paths",
                    "Configure component islands for interactivity",
                    "Enable authentication and deploy"
                ],
                "template_features": [
                    "Component islands architecture",
                    "Framework-agnostic components (React/Vue/Svelte)",
                    "Zero JavaScript by default",
                    "Modern build optimizations"
                ],
                "best_for": "Modern interactive sites, component showcases"
            },
            "hugo": {
                "title": "Hugo + Decap CMS Setup",
                "complexity": "Technical",
                "setup_time": "2-3 hours",
                "steps": [
                    "Configure Hugo content types and sections",
                    "Set up Decap CMS config for Hugo structure",
                    "Configure taxonomies and content organization",
                    "Deploy high-performance static site"
                ],
                "template_features": [
                    "Extremely fast builds (< 5 seconds)",
                    "Excellent for large content sites",
                    "Go-powered performance",
                    "Advanced content organization"
                ],
                "best_for": "Documentation sites, large blogs, performance-critical content"
            },
            "gatsby": {
                "title": "Gatsby + Decap CMS Setup",
                "complexity": "Advanced",
                "setup_time": "4-5 hours",
                "steps": [
                    "Configure Gatsby's GraphQL data layer",
                    "Set up gatsby-plugin-netlify-cms",
                    "Configure content sourcing and transformations",
                    "Deploy React-powered static site"
                ],
                "template_features": [
                    "React-based templates",
                    "GraphQL data integration",
                    "Rich plugin ecosystem",
                    "Progressive web app features"
                ],
                "best_for": "Content-heavy sites, React developers, PWA requirements"
            }
        }

        return guides.get(self.ssg_config.ssg_engine, {"title": "Generic Decap CMS Setup"})
```

#### 2.2 Tina CMS Stack
**File**: `stacks/cms/tina_cms_stack.py`

```python
class TinaCMSStack(BaseCMSStack):
    """
    Tina CMS stack supporting multiple SSG engines.

    Compatible SSG Engines: Astro, Next.js, Nuxt, Eleventy
    Management Model: Visual editing with live preview
    Monthly Cost: $60-85 (hosting + Tina Cloud $0-29)
    Setup Cost: $1,200-3,600 (varies by SSG complexity)
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        client_id: str,
        domain: str,
        ssg_engine: str = "astro",  # Astro default for best Tina experience
        **kwargs
    ):
        super().__init__(
            scope, construct_id, client_id, domain,
            cms_provider="tina",
            ssg_engine=ssg_engine,
            **kwargs
        )

    def _setup_cms_integration(self):
        """Set up Tina CMS specific infrastructure"""
        # Base Tina configuration
        tina_vars = {
            "CMS_PROVIDER": "tina",
            "TINA_CMS_ENABLED": "true",
            "TINA_CLIENT_ID": "${TINA_CLIENT_ID}",    # CDK parameter
            "TINA_TOKEN": "${TINA_TOKEN}",            # CDK parameter
            "TINA_BRANCH": "main",
            "TINA_CONFIG_PATH": "tina/config.ts"
        }

        # SSG-specific Tina configuration
        ssg_specific_vars = self._get_ssg_specific_tina_config()
        tina_vars.update(ssg_specific_vars)

        self.add_environment_variables(tina_vars)

    def _get_ssg_specific_tina_config(self) -> Dict[str, str]:
        """Get SSG-specific Tina CMS configuration"""
        ssg_configs = {
            "astro": {
                "PUBLIC_TINA_CLIENT_ID": "${TINA_CLIENT_ID}",
                "ASTRO_TINA_INTEGRATION": "true",
                "TINA_CONTENT_PATH": "src/content"
            },
            "nextjs": {
                "TINA_PUBLIC_IS_LOCAL": "false",
                "NEXT_PUBLIC_TINA_CLIENT_ID": "${TINA_CLIENT_ID}",
                "NEXTJS_TINA_INTEGRATION": "true",
                "TINA_CONTENT_PATH": "content"
            },
            "nuxt": {
                "NUXT_PUBLIC_TINA_CLIENT_ID": "${TINA_CLIENT_ID}",
                "NUXT_TINA_INTEGRATION": "true",
                "TINA_CONTENT_PATH": "content"
            },
            "eleventy": {
                "TINA_CONTENT_PATH": "src/_data",
                "ELEVENTY_TINA_INTEGRATION": "true"
            }
        }

        return ssg_configs.get(self.ssg_config.ssg_engine, {})
```

#### 2.3 Sanity & Contentful Stacks
Similar implementation pattern for `SanityCMSStack` and `ContentfulStack`.

### **Phase 3: Enhanced Factory System (Week 3)**

#### 3.1 CMS Stack Factory
**File**: `stacks/shared/cms_stack_factory.py`

```python
class CMSStackFactory:
    """Factory for creating CMS stacks with flexible SSG engine support"""

    CMS_STACK_CLASSES = {
        "decap": DecapCMSStack,
        "tina": TinaCMSStack,
        "sanity": SanityCMSStack,
        "contentful": ContentfulStack
    }

    @classmethod
    def create_cms_stack(
        cls,
        scope: Construct,
        client_id: str,
        domain: str,
        cms_provider: str,
        ssg_engine: str = "eleventy",
        **kwargs
    ):
        """Create CMS stack with specified SSG engine"""

        # Validate CMS provider
        stack_class = cls.CMS_STACK_CLASSES.get(cms_provider)
        if not stack_class:
            available_cms = list(cls.CMS_STACK_CLASSES.keys())
            raise ValueError(f"Unsupported CMS provider '{cms_provider}'. Available: {available_cms}")

        # Generate construct ID
        construct_id = f"{client_id.title()}-{cms_provider.title()}-{ssg_engine.title()}-Stack"

        return stack_class(
            scope=scope,
            construct_id=construct_id,
            client_id=client_id,
            domain=domain,
            ssg_engine=ssg_engine,
            **kwargs
        )

    @classmethod
    def get_compatible_ssg_engines(cls, cms_provider: str) -> List[str]:
        """Get list of SSG engines compatible with CMS provider"""
        return BaseCMSStack.COMPATIBLE_SSG_ENGINES.get(cms_provider, [])

    @classmethod
    def validate_compatibility(cls, cms_provider: str, ssg_engine: str) -> bool:
        """Check if SSG engine is compatible with CMS provider"""
        compatible_engines = cls.get_compatible_ssg_engines(cms_provider)
        return ssg_engine in compatible_engines

    @classmethod
    def get_cms_recommendations(cls, requirements: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get CMS + SSG recommendations based on client requirements"""
        recommendations = []

        # Budget-conscious recommendations
        if requirements.get("budget_conscious"):
            recommendations.append({
                "cms": "decap",
                "ssg_options": ["eleventy", "hugo"],
                "monthly_cost": "$50-75",
                "setup_cost": "$960-1,800",
                "reason": "Free CMS with fast, simple SSG engines",
                "best_for": "Small businesses, blogs, simple content sites"
            })

        # Visual editing preferences
        if requirements.get("visual_editing"):
            recommendations.append({
                "cms": "tina",
                "ssg_options": ["astro", "nextjs"],
                "monthly_cost": "$60-85",
                "setup_cost": "$1,200-3,600",
                "reason": "Visual editing with modern SSG performance",
                "best_for": "Content creators, modern businesses"
            })

        # Enterprise needs
        if requirements.get("enterprise_features"):
            recommendations.append({
                "cms": "contentful",
                "ssg_options": ["gatsby", "nextjs"],
                "monthly_cost": "$375+",
                "setup_cost": "$2,400-4,800",
                "reason": "Enterprise CMS with advanced features",
                "best_for": "Large organizations, complex content workflows"
            })

        # Performance critical
        if requirements.get("performance_critical"):
            recommendations.append({
                "cms": "decap",
                "ssg_options": ["hugo", "astro"],
                "monthly_cost": "$50-75",
                "setup_cost": "$960-2,400",
                "reason": "Fastest SSG engines with efficient CMS",
                "best_for": "Large content sites, documentation, speed-critical applications"
            })

        return recommendations

    @classmethod
    def get_pricing_matrix(cls) -> Dict[str, Any]:
        """Get comprehensive pricing matrix for all CMS/SSG combinations"""
        pricing_matrix = {}

        for cms_provider, stack_class in cls.CMS_STACK_CLASSES.items():
            compatible_engines = cls.get_compatible_ssg_engines(cms_provider)

            pricing_matrix[cms_provider] = {
                "monthly_cost_range": cls._get_cms_monthly_cost(cms_provider),
                "ssg_options": {}
            }

            for ssg_engine in compatible_engines:
                pricing_matrix[cms_provider]["ssg_options"][ssg_engine] = {
                    "setup_cost": cls._get_setup_cost(cms_provider, ssg_engine),
                    "complexity": cls._get_complexity_level(cms_provider, ssg_engine),
                    "estimated_hours": cls._get_estimated_hours(cms_provider, ssg_engine)
                }

        return pricing_matrix
```

#### 3.2 Client-Facing Usage Examples
```python
# Example usage after refactoring:

# Client wants budget-friendly CMS with fast builds
decap_hugo_stack = CMSStackFactory.create_cms_stack(
    scope=app,
    client_id="budget-client",
    domain="budget.com",
    cms_provider="decap",
    ssg_engine="hugo"  # Fastest builds
)

# Client wants modern interactivity with visual editing
tina_astro_stack = CMSStackFactory.create_cms_stack(
    scope=app,
    client_id="modern-business",
    domain="modern.com",
    cms_provider="tina",
    ssg_engine="astro"  # Component islands + visual editing
)

# Get recommendations for specific client needs
recommendations = CMSStackFactory.get_cms_recommendations({
    "budget_conscious": True,
    "content_heavy": True,
    "performance_critical": True
})

# Check compatibility before creating stack
if CMSStackFactory.validate_compatibility("contentful", "gatsby"):
    stack = CMSStackFactory.create_cms_stack(
        scope=app,
        client_id="enterprise-client",
        domain="enterprise.com",
        cms_provider="contentful",
        ssg_engine="gatsby"
    )
```

### **Phase 4: Template System Updates (Week 4)**

#### 4.1 Template Repository Structure
```
templates/
├── decap-cms/
│   ├── eleventy-decap-business/     # Eleventy + Decap business template
│   ├── astro-decap-interactive/     # Astro + Decap modern template
│   ├── hugo-decap-performance/      # Hugo + Decap documentation template
│   └── gatsby-decap-content/        # Gatsby + Decap content-heavy template
├── tina-cms/
│   ├── astro-tina-visual/           # Astro + Tina visual editing
│   ├── nextjs-tina-react/           # Next.js + Tina React ecosystem
│   ├── nuxt-tina-vue/               # Nuxt + Tina Vue ecosystem
│   └── eleventy-tina-simple/        # Eleventy + Tina simple setup
├── sanity-cms/
│   ├── astro-sanity-structured/     # Astro + Sanity structured content
│   ├── gatsby-sanity-graphql/       # Gatsby + Sanity GraphQL integration
│   ├── nextjs-sanity-react/         # Next.js + Sanity React
│   └── nuxt-sanity-vue/             # Nuxt + Sanity Vue
└── contentful/
    ├── gatsby-contentful-enterprise/ # Gatsby + Contentful enterprise
    ├── astro-contentful-performance/ # Astro + Contentful performance
    ├── nextjs-contentful-react/      # Next.js + Contentful React
    └── nuxt-contentful-vue/          # Nuxt + Contentful Vue
```

#### 4.2 Template Configuration Files
Each template includes SSG-specific CMS configuration:

**Eleventy + Decap Example:**
```yaml
# admin/config.yml
backend:
  name: git-gateway
  branch: main

media_folder: "src/assets/images"
public_folder: "/images"

collections:
  - name: "posts"
    label: "Blog Posts"
    folder: "src/posts"
    create: true
    slug: "{{year}}-{{month}}-{{day}}-{{slug}}"
    fields:
      - {label: "Title", name: "title", widget: "string"}
      - {label: "Date", name: "date", widget: "datetime"}
      - {label: "Body", name: "body", widget: "markdown"}
```

**Astro + Decap Example:**
```yaml
# admin/config.yml
backend:
  name: git-gateway
  branch: main

media_folder: "src/assets/images"
public_folder: "/images"

collections:
  - name: "blog"
    label: "Blog Posts"
    folder: "src/content/blog"
    create: true
    slug: "{{slug}}"
    fields:
      - {label: "Title", name: "title", widget: "string"}
      - {label: "Date", name: "pubDate", widget: "datetime"}
      - {label: "Description", name: "description", widget: "text"}
      - {label: "Body", name: "body", widget: "markdown"}
```

### **Phase 5: Testing & Documentation (Week 5)**

#### 5.1 Comprehensive Testing Strategy
```python
# tests/test_cms_stack_flexibility.py
class TestCMSStackFlexibility:
    """Test flexible CMS/SSG combinations"""

    @pytest.mark.parametrize("cms,ssg", [
        ("decap", "eleventy"),
        ("decap", "astro"),
        ("decap", "hugo"),
        ("tina", "astro"),
        ("tina", "nextjs"),
        ("sanity", "astro"),
        ("contentful", "gatsby")
    ])
    def test_valid_cms_ssg_combinations(self, cms, ssg):
        """Test that valid CMS/SSG combinations work"""
        stack = CMSStackFactory.create_cms_stack(
            scope=self.app,
            client_id="test-client",
            domain="test.com",
            cms_provider=cms,
            ssg_engine=ssg
        )
        assert stack is not None
        assert stack.ssg_config.ssg_engine == ssg
        assert stack.ssg_config.cms_provider == cms

    def test_invalid_cms_ssg_combination(self):
        """Test that invalid combinations raise errors"""
        with pytest.raises(ValueError):
            CMSStackFactory.create_cms_stack(
                scope=self.app,
                client_id="test-client",
                domain="test.com",
                cms_provider="decap",
                ssg_engine="invalid_engine"
            )

    def test_template_variant_resolution(self):
        """Test that template variants resolve correctly"""
        stack = CMSStackFactory.create_cms_stack(
            scope=self.app,
            client_id="test-client",
            domain="test.com",
            cms_provider="decap",
            ssg_engine="astro"
        )
        assert stack.ssg_config.template_variant == "decap_cms_interactive"

    def test_cms_recommendations(self):
        """Test recommendation engine"""
        recommendations = CMSStackFactory.get_cms_recommendations({
            "budget_conscious": True,
            "performance_critical": True
        })

        assert len(recommendations) > 0
        assert any(rec["cms"] == "decap" for rec in recommendations)
        assert any("hugo" in rec["ssg_options"] for rec in recommendations)
```

#### 5.2 Documentation Updates
- Update SSG_INTEGRATION_GUIDE.md with flexible architecture
- Create client guidance on choosing SSG engines within CMS tiers
- Add architectural decision records (ADRs) for design choices
- Create setup guides for each SSG/CMS combination

---

## 📊 **Business Impact Analysis**

### **Before Refactoring (Current State)**
- **4 hardcoded stacks** with arbitrary SSG/CMS pairings
- **Limited client choice** - forced to accept specific combinations
- **Code duplication** - need separate classes for each combination
- **Revenue constraints** - single price point per arbitrary pairing

### **After Refactoring (Target State)**
- **15+ flexible combinations** from 4 CMS-focused classes
- **Client choice within tiers** - select SSG based on technical comfort
- **Reduced code duplication** - CMS logic centralized, SSG parameterized
- **Better revenue targeting** - same monthly cost serves different complexity levels

### **Revenue Impact**
**Decap CMS Tier Example (Monthly: $50-75)**
- **Before**: Only `Eleventy + Decap` → Single technical level
- **After**: `Hugo + Decap` (Technical), `Eleventy + Decap` (Intermediate), `Astro + Decap` (Advanced), `Gatsby + Decap` (Expert)
- **Result**: Same monthly revenue serves 4x client technical comfort levels

### **Client Satisfaction Impact**
- **Increased Choice**: Clients choose SSG based on preferences, not arbitrary constraints
- **Better Value Alignment**: Technical comfort level matches complexity and setup cost
- **Future Flexibility**: Easy to add new SSG engines without restructuring pricing

---

## 🎯 **Success Metrics**

### **Technical Metrics**
- **Code Reduction**: From 20+ hardcoded classes to 4 flexible classes
- **Template Coverage**: 15+ SSG/CMS combinations from unified template system
- **Compatibility Matrix**: 100% coverage of technically viable combinations

### **Business Metrics**
- **Client Choice Increase**: From 4 fixed options to 15+ flexible combinations
- **Revenue Flexibility**: Same monthly tiers serve multiple technical levels
- **Setup Cost Optimization**: Better alignment between complexity and pricing

### **Client Experience Metrics**
- **Choice Satisfaction**: Clients select SSG based on technical comfort and requirements
- **Implementation Alignment**: Setup complexity matches client technical capabilities
- **Future Adaptability**: Easy addition of new SSG engines without pricing restructuring

---

## 🚀 **Implementation Timeline**

| Week | Phase | Key Deliverables | Success Criteria |
|------|-------|------------------|------------------|
| **1** | Architecture Foundation | `BaseCMSStack`, compatibility matrix, validation | Template resolution working for all combinations |
| **2** | Concrete CMS Stacks | `DecapCMSStack`, `TinaCMSStack`, etc. | All 4 CMS stacks accept multiple SSG engines |
| **3** | Factory System | `CMSStackFactory`, recommendations engine | Factory creates any valid SSG/CMS combination |
| **4** | Template System | Template variants for all combinations | 15+ template repositories ready for deployment |
| **5** | Testing & Documentation | Comprehensive tests, client guidance | All combinations tested and documented |

---

## 🔮 **Future Extensibility**

### **Adding New SSG Engines**
```python
# Easy to add new SSG engines to existing CMS stacks
COMPATIBLE_SSG_ENGINES = {
    "decap": ["eleventy", "astro", "hugo", "gatsby", "remix"],  # Added Remix
    # ... other CMS providers
}
```

### **Adding New CMS Providers**
```python
# Easy to add new CMS providers with SSG compatibility
class StrapeCMSStack(BaseCMSStack):  # New CMS provider
    COMPATIBLE_SSG_ENGINES = ["astro", "nextjs", "nuxt"]
```

### **Client-Specific Customizations**
```python
# Support client-specific SSG/CMS configurations
custom_stack = CMSStackFactory.create_cms_stack(
    cms_provider="decap",
    ssg_engine="astro",
    custom_config={
        "enable_advanced_features": True,
        "custom_theme": "client_branded_theme"
    }
)
```

---

**Document Status**: Planning Phase
**Next Action**: Implement Phase 1 - Architecture Foundation
**Approval Required**: Technical architecture review and business impact validation