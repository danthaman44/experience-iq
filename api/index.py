"""
Legacy index.py - Re-exports the main application for backward compatibility.
This file maintains compatibility with existing Vercel deployments.
"""

from api.main import app

__all__ = ["app"]
