"""
A2A SDK Compatibility Patch (GIVEN - fully implemented)
Workaround for google-adk==1.9.0 compatibility with a2a-sdk==0.3.0

This patch addresses the issue where google-adk tries to import A2ACardResolver
from a2a.client.client, but in a2a-sdk==0.3.0 it's in a2a.client.card_resolver.

Reference: https://github.com/google/adk-python/pull/2297
This workaround can be removed when google-adk version > 1.9.0 is released.
"""

import sys
from typing import Any

import a2a.client as client_package
import a2a.client.errors as client_errors
from a2a.client import client as real_client_module
from a2a.client.card_resolver import A2ACardResolver


class PatchedClientModule:
    """Patched client module that adds A2ACardResolver to the correct location."""

    def __init__(self, real_module) -> None:
        # Copy all non-private attributes from the real module
        for attr in dir(real_module):
            if not attr.startswith("_"):
                setattr(self, attr, getattr(real_module, attr))

        # Add A2ACardResolver to this module
        self.A2ACardResolver = A2ACardResolver


# Apply the patch by replacing the module in sys.modules
patched_module = PatchedClientModule(real_client_module)
sys.modules["a2a.client.client"] = patched_module  # type: ignore

# Some environments provide an a2a version where ClientEvent is no longer
# exported from a2a.client. google-adk 1.9.0 still imports this symbol, so
# expose a safe placeholder when missing.
if not hasattr(client_package, "ClientEvent"):
    client_package.ClientEvent = Any  # type: ignore[attr-defined]

# google-adk imports A2AClientHTTPError, but some a2a versions expose only
# A2AClientError. Provide an alias for compatibility.
if not hasattr(client_errors, "A2AClientHTTPError"):
    client_errors.A2AClientHTTPError = client_errors.A2AClientError  # type: ignore[attr-defined]

# Make the patch discoverable
__all__ = ["patched_module", "A2ACardResolver"]
