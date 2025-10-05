#!/usr/bin/env python3
"""
Web Services Infrastructure CDK Application

Main entry point for AWS CDK infrastructure deployment.
Week 1: Basic shared infrastructure deployment.
"""

import aws_cdk as cdk
from stacks.shared import SharedInfraStack


def main():
    """Main entry point for CDK application."""
    app = cdk.App()
    
    # Deploy shared infrastructure
    SharedInfraStack(
        app,
        "WebServices-SharedInfra",
        description="Shared operational infrastructure for web services business",
        env=cdk.Environment(
            account=app.node.try_get_context("account"),
            region=app.node.try_get_context("region") or "us-east-1"
        )
    )
    
    app.synth()


if __name__ == "__main__":
    main()