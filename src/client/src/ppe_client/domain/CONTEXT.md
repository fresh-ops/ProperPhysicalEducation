# Module: domain

## Responsibility
This module is responsible for the domain logic. It **must not** know about:
- Network interactions
- Database models
- External APIs
- User Interface

## Rules
1. **Dependencies**: Only Python standard library is allowed. No external packages(unless stated in *Allowed Dependencies*).
2. **Imports**: Only imports from this layer are allowed.
3. **Side Effects**: This module **must** be pure. No network, no I/O, no network calls.

## Key Entities
- `CameraDescriptor`: a cross-module description of the camera entity.
- `CameraIdentity`: an identity of the camera device. Should be used to distinguish between different cameras.