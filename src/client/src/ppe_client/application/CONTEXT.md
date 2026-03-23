# Module: application

## Responsibility
This is responsible for wiring layers. It provides contracts, but **does not** implement them.

## Rules
1. **Dependencies**: Only Python standard library is allowed. No external packages(unless stated in *Allowed Dependencies*).
2. **Imports**: It is allowed to import modules from the *domain* layer. 
3. **Side Effects**: This module **must** be pure. It **must not** have any state. The Network, I/O operations, etc. should be provided via *ports*.