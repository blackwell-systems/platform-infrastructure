# Claude AI Steering Guide for Platform Infrastructure

## 🎯 Project Context
This is a multi-client web development services infrastructure built with AWS CDK. When working on this project, always consider the tier-based client model (individual → business → enterprise) and maintain consistency across all implementations.

## 🐍 Python Environment Expectations

### Always Use These Standards
- **Python Version**: 3.13+ (project requires 3.13)
- **Package Manager**: Use `uv` commands exclusively - never suggest pip, poetry, or conda
- **Dependencies**: Always use `uv add` for new packages, `uv sync` for installation
- **Execution**: Use `uv run python` or `uv run [command]` for all Python execution
- **Virtual Environment**: Single `.venv` in project root managed by uv

### Key Commands to Use
```bash
uv sync                    # Install/update dependencies
uv run python app.py       # Execute Python with project deps
uv add package-name        # Add new dependency
uv run pytest             # Run tests
uv run black .             # Format code
uv run ruff check .        # Lint code
```

## 📋 Pydantic Model Requirements

### ALWAYS Follow These Patterns
When creating or modifying Pydantic models:

1. **Use Modern Pydantic v2 Syntax**
```python
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Literal
from enum import Enum

class YourModel(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        # Always include examples for complex models
        json_schema_extra={
            "examples": [{"field": "example_value"}]
        }
    )
```

2. **Required Field Patterns**
```python
field_name: str = Field(
    ...,  # Required field marker
    description="Clear description of what this field represents",
    pattern=r"^[a-z0-9-]+$"  # Add validation patterns when appropriate
)
```

3. **Optional Field Patterns**
```python
optional_field: Optional[str] = Field(
    default=None,
    description="Clear description including when None is appropriate"
)

# OR with meaningful defaults
enabled_feature: bool = Field(
    default=True,
    description="Description of what this feature controls"
)
```

4. **Always Use Enums for Choices**
```python
class ClientTier(str, Enum):
    TIER1_INDIVIDUAL = "tier1-individual"
    TIER2_BUSINESS = "tier2-business"
    TIER3_ENTERPRISE = "tier3-enterprise"
```

5. **Use @computed_field for Derived Values**
```python
@computed_field
@property
def stack_name(self) -> str:
    """Generate consistent stack naming."""
    return f"WebServices-{self.client_id.title().replace('-', '')}"
```

### Model Organization Rules
- Base models in `models/base.py`
- Client-specific models in `models/client.py`
- Infrastructure models in `models/infrastructure.py`
- Always inherit from a base configuration class

## 🏗️ AWS CDK Conventions

### Stack Creation Pattern
When creating CDK stacks, ALWAYS use this structure:

```python
from aws_cdk import Stack, App
from constructs import Construct
from models.client import ClientConfig

class YourStack(Stack):
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        client_config: ClientConfig,  # Always accept client config
        **kwargs
    ):
        super().__init__(scope, construct_id, **kwargs)

        self.client_config = client_config

        # Break into logical methods
        self._create_storage_resources()
        self._create_networking_resources()
        self._create_compute_resources()
```

### Resource Naming Standards
- **CDK Construct IDs**: PascalCase (e.g., "ContentBucket")
- **AWS Resource Names**: kebab-case with client prefix (e.g., "acme-corp-content-bucket")
- **Always use client_id as prefix**: `f"{client_config.client_id}-{resource-type}"`

### Import Conventions
```python
# CDK v2 imports - always use this pattern
from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_route53 as route53,
)
from constructs import Construct
```

## 📁 File Organization Rules

### When Adding New Files
- **Models**: Always go in `models/` directory
- **Stacks**: Organize by tier in `stacks/{tier-name}/`
- **Reusable constructs**: Go in `constructs/`
- **Utilities**: Go in `shared/`
- **Client configs**: Go in `clients/{client-name}/`
- **Tools**: Operational scripts go in `tools/`

### File Naming Conventions
- Use snake_case for Python files
- Use kebab-case for client directories
- Use descriptive names: `static_site_construct.py` not `construct.py`

## 🧪 Testing Requirements

### Always Create Tests When
- Adding new Pydantic models
- Creating new CDK constructs
- Adding utility functions
- Modifying client configuration logic

### Test Structure Pattern
```python
import pytest
from pydantic import ValidationError
from models.your_model import YourModel

class TestYourModel:
    """Test your model with clear descriptions."""

    def test_valid_configuration(self):
        """Test that valid inputs create proper model."""
        # Test implementation

    def test_invalid_input_validation(self):
        """Test that invalid inputs raise ValidationError."""
        with pytest.raises(ValidationError):
            # Test implementation

    @pytest.mark.parametrize("input,expected", [
        ("valid-input", True),
        ("invalid input", False),
    ])
    def test_input_validation_cases(self, input, expected):
        """Test multiple validation scenarios."""
        # Test implementation
```

## 🚨 Critical Requirements

### NEVER Do These Things
- Don't use pip, poetry, or conda - only uv
- Don't create models without validation
- Don't create AWS resources without client prefixes
- Don't hardcode values that should be configurable
- Don't skip type hints on functions
- Don't create files outside the established directory structure

### ALWAYS Do These Things
- Use type hints on all functions and methods
- Add docstrings to all classes and public methods
- Validate all inputs with Pydantic models
- Use descriptive variable and function names
- Follow the established naming conventions
- Add appropriate error handling
- Include examples in model configurations

## 🔧 Code Quality Standards

### When Writing New Code
1. **Type Everything**: All parameters, return values, and variables should have type hints
2. **Document Everything**: Public APIs need docstrings explaining purpose, args, returns, and raises
3. **Validate Everything**: Use Pydantic for all data structures and configurations
4. **Test Everything**: Write tests for new functionality

### Code Review Self-Check
Before suggesting code changes, verify:
- [ ] Uses uv for all Python package management
- [ ] Follows Pydantic v2 patterns correctly
- [ ] Has proper type hints
- [ ] Includes appropriate validation
- [ ] Uses established naming conventions
- [ ] Includes tests for new functionality
- [ ] Has clear docstrings

## 🎨 Response Patterns

### When Suggesting New Features
1. **Start with the Pydantic model** - define the data structure and validation first
2. **Create the CDK construct** - implement the infrastructure component
3. **Add tests** - ensure the functionality works correctly
4. **Update documentation** - explain how to use the new feature

### When Fixing Issues
1. **Identify the root cause** - don't just fix symptoms
2. **Update models if needed** - ensure validation catches the issue
3. **Add tests** - prevent regression
4. **Consider tier-specific impacts** - how does this affect different client tiers?

### When Adding Dependencies
- Always use `uv add package-name`
- Explain why the dependency is needed
- Consider if it affects all tiers or specific ones
- Update any relevant models or configurations

## 📋 Project-Specific Context

### Client Tier System
- **Tier 1 (Individual)**: Basic static hosting, limited features
- **Tier 2 (Business)**: Enhanced features, custom domains, basic CDN
- **Tier 3 (Enterprise)**: Full feature set, advanced CDN, custom integrations

### SSG Engine Support
The project supports multiple Static Site Generators:
- Hugo, Eleventy, Astro, Jekyll, Nuxt, Next.js, Gatsby
- Always consider SSG compatibility when adding features
- Use the `SSGEngine` enum from `shared/ssg_engines.py`

### AWS Services in Use
- **S3**: Content storage and static hosting
- **CloudFront**: CDN distribution
- **Route53**: DNS management
- **Certificate Manager**: SSL certificates
- **Lambda**: Build and deployment functions

## 🚀 Deployment Considerations

### When Creating Infrastructure Code
- Always consider multi-environment deployment (dev/staging/prod)
- Use environment-specific configurations
- Ensure resources can be torn down cleanly
- Consider cost implications across client tiers

### When Adding New Client Types
- Update the `ClientTier` enum
- Create tier-specific stack configurations
- Add appropriate validation rules
- Consider pricing and resource limits

---

## 🎯 Summary for Claude

When working on this project:
1. **Use uv exclusively** for Python package management
2. **Follow Pydantic v2 patterns** with proper validation and type hints
3. **Maintain the tier-based client model** in all implementations
4. **Use established naming conventions** for consistency
5. **Create tests** for all new functionality
6. **Document clearly** with docstrings and type hints
7. **Consider AWS costs** and multi-environment deployment

This project values explicit, well-validated, and properly structured code over quick implementations. Always prioritize clarity and maintainability.