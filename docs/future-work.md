# Deferred Production Fixes

The following issues were observed in the current production deployment but are NOT addressed in this scaffold. They are tracked here for future work.

1. **Cancellation inconsistency**: Parcel cancellation flow has inconsistent behavior between frontend and backend.
2. **Missing parcel weight**: Weight input UI not fully implemented.
3. **Invalid Date rendering**: Date fields render as "Invalid Date" in some views.
4. **Price-format mismatch**: Price display format differs between frontend and backend.
5. **Missing destination-editing UI**: Destination change form exists but API endpoint needs verification.
6. **Admin-role deployment issue**: Admin role assignment or checking has deployment-related bugs.
7. **Branding issue**: UI branding elements need alignment.

These will be addressed in a dedicated bug-fix phase after the scaffold is verified and merged.
