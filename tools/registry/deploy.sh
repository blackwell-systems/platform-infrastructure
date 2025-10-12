#!/bin/bash
"""
Provider Registry Deployment Wrapper Script

Simple wrapper for registry deployment with common configuration options.
Designed for CI/CD integration and local development.

Usage:
    ./deploy.sh                    # Deploy with environment variables
    ./deploy.sh --dry-run          # Test deployment
    ./deploy.sh --help             # Show help
"""

set -e  # Exit on error

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Default configuration
DEFAULT_BUCKET_NAME="${REGISTRY_BUCKET_NAME:-blackwell-provider-registry}"
DEFAULT_DISTRIBUTION_ID="${REGISTRY_DISTRIBUTION_ID:-}"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

show_help() {
    cat << EOF
Provider Registry Deployment Script

USAGE:
    $0 [OPTIONS]

OPTIONS:
    --bucket-name NAME      S3 bucket name (default: $DEFAULT_BUCKET_NAME)
    --distribution-id ID    CloudFront distribution ID
    --dry-run              Test deployment without making changes
    --verbose              Enable verbose logging
    --help                 Show this help message

ENVIRONMENT VARIABLES:
    REGISTRY_BUCKET_NAME        Default S3 bucket name
    REGISTRY_DISTRIBUTION_ID    Default CloudFront distribution ID
    AWS_PROFILE                AWS profile to use
    AWS_REGION                 AWS region (default: us-east-1)

EXAMPLES:
    # Deploy with defaults
    $0

    # Test deployment
    $0 --dry-run

    # Deploy to specific bucket and distribution
    $0 --bucket-name my-bucket --distribution-id E1234567890

    # Use specific AWS profile
    AWS_PROFILE=production $0

EOF
}

check_dependencies() {
    log_info "Checking dependencies..."

    # Check Python and uv
    if ! command -v python3 &> /dev/null; then
        log_error "python3 is required but not installed"
        exit 1
    fi

    if ! command -v uv &> /dev/null; then
        log_error "uv is required but not installed"
        exit 1
    fi

    # Check AWS CLI (optional but helpful)
    if ! command -v aws &> /dev/null; then
        log_warn "AWS CLI not found - deployment will use boto3 directly"
    else
        log_info "AWS CLI found: $(aws --version 2>&1 | head -n1)"
    fi

    # Check AWS credentials
    if [[ -z "${AWS_ACCESS_KEY_ID:-}" ]] && [[ -z "${AWS_PROFILE:-}" ]] && [[ ! -f ~/.aws/credentials ]]; then
        log_warn "No AWS credentials detected. Make sure to configure AWS access."
    fi

    log_info "Dependencies check complete"
}

validate_environment() {
    log_info "Validating environment..."

    # Set default region if not specified
    export AWS_DEFAULT_REGION="${AWS_REGION:-us-east-1}"

    # Check if registry output directory exists
    if [[ ! -d "$SCRIPT_DIR/output" ]]; then
        log_error "Registry output directory not found: $SCRIPT_DIR/output"
        log_error "Run extract_metadata.py first to generate registry data"
        exit 1
    fi

    # Count JSON files
    json_count=$(find "$SCRIPT_DIR/output" -name "*.json" | wc -l)
    log_info "Found $json_count JSON files to deploy"

    if [[ $json_count -eq 0 ]]; then
        log_error "No JSON files found in output directory"
        exit 1
    fi

    log_info "Environment validation complete"
}

main() {
    local bucket_name="$DEFAULT_BUCKET_NAME"
    local distribution_id="$DEFAULT_DISTRIBUTION_ID"
    local dry_run=false
    local verbose=false

    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --bucket-name)
                bucket_name="$2"
                shift 2
                ;;
            --distribution-id)
                distribution_id="$2"
                shift 2
                ;;
            --dry-run)
                dry_run=true
                shift
                ;;
            --verbose)
                verbose=true
                shift
                ;;
            --help)
                show_help
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done

    # Validate bucket name
    if [[ -z "$bucket_name" ]]; then
        log_error "Bucket name is required"
        log_error "Provide via --bucket-name or set REGISTRY_BUCKET_NAME environment variable"
        exit 1
    fi

    log_info "Starting Provider Registry deployment"
    log_info "Bucket: $bucket_name"
    [[ -n "$distribution_id" ]] && log_info "Distribution: $distribution_id"
    [[ "$dry_run" == true ]] && log_warn "DRY RUN MODE - No changes will be made"

    # Pre-deployment checks
    check_dependencies
    validate_environment

    # Build Python command
    local python_cmd="uv run python $SCRIPT_DIR/deploy_registry.py --bucket-name \"$bucket_name\""

    if [[ -n "$distribution_id" ]]; then
        python_cmd="$python_cmd --distribution-id \"$distribution_id\""
    fi

    if [[ "$dry_run" == true ]]; then
        python_cmd="$python_cmd --dry-run"
    fi

    if [[ "$verbose" == true ]]; then
        python_cmd="$python_cmd --verbose"
    fi

    # Execute deployment
    log_info "Executing deployment command:"
    log_info "$python_cmd"
    echo

    if eval "$python_cmd"; then
        log_info "🎉 Registry deployment completed successfully!"
        echo
        log_info "Registry URL: https://${distribution_id:-$bucket_name.s3.amazonaws.com}"
        log_info "Test manifest: curl https://${distribution_id:-$bucket_name.s3.amazonaws.com}/manifest.json"
    else
        log_error "❌ Registry deployment failed"
        exit 1
    fi
}

# Execute main function with all arguments
main "$@"