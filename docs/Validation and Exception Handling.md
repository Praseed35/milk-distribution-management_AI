# Chapter 9 – Validation and Exception Handling

---

# 1. Introduction

Validation and Exception Handling ensure that the Milk Distribution ERP processes only valid business data while preventing incorrect, duplicate, or inconsistent transactions.

The ERP validates every request before saving it to the database. If validation fails or a business rule is violated, the system returns a meaningful error message without affecting existing data.

This approach improves data integrity, simplifies troubleshooting, and provides a better user experience.

---

# 2. Validation Objectives

The Validation module is designed to:

* Prevent invalid data entry.
* Maintain database integrity.
* Enforce business rules.
* Prevent duplicate records.
* Improve user experience.
* Protect business data.
* Ensure reliable reporting.
* Support secure API operations.

---

# 3. Types of Validation

The ERP performs multiple levels of validation.

### Input Validation

Verifies user input before processing.

Examples:

* Required fields
* Data type validation
* String length validation
* Numeric validation

---

### Business Validation

Verifies business rules.

Examples:

* Route must exist.
* Route must be active.
* Customer must exist.
* Token Book must be active.

---

### Database Validation

Performed before saving data.

Examples:

* Duplicate phone numbers
* Duplicate token sheets
* Duplicate customer codes
* Foreign key validation

---

### Security Validation

Protects APIs.

Examples:

* JWT Token Validation
* User Authentication
* User Authorization
* Active User Verification

---

# 4. Customer Module Validation

When creating or updating a customer, the ERP validates:

* Customer name is required.
* Primary phone is required.
* Primary phone must be unique.
* Primary and alternate phone cannot be the same.
* Assigned route must exist.
* Assigned route must be active.

Possible exceptions:

* CustomerNotFoundError
* DuplicatePrimaryPhoneError
* SamePhoneNumberError
* RouteNotFoundError
* InactiveRouteError

---

# 5. Route Module Validation

The Route module validates:

* Route code is required.
* Route name is required.
* Route code must be unique.
* Route name must be unique.

Possible exceptions:

* RouteNotFoundError
* DuplicateRouteCodeError
* DuplicateRouteNameError

---

# 6. Milk Type Validation

The ERP validates:

* Milk type exists.
* Milk type is active.
* Capacity is valid.

Possible exceptions:

* MilkTypeNotFoundError
* InactiveMilkTypeError

---

# 7. Subscription Validation

The Subscription module validates:

* Customer exists.
* Milk type exists.
* Quantity is greater than zero.
* Shift is valid.
* Duplicate subscriptions are not created.

Possible exceptions:

* SubscriptionNotFoundError
* InvalidShiftError
* DuplicateSubscriptionError
* InactiveCustomerError
* InactiveMilkTypeError
* InvalidSubscriptionQuantityError
* SubscriptionAlreadyInactiveError

---

# 8. Delivery Exception Validation

The Delivery Exception module validates:

* Subscription exists and is active.
* End date is after start date (if provided).
* No overlapping exceptions exist for the same subscription.
* Exception type is valid.

Possible exceptions:

* DeliveryExceptionNotFoundError
* InactiveSubscriptionError
* InvalidDeliveryExceptionDateError
* DeliveryExceptionOverlapError
* DeliveryExceptionAlreadyInactiveError

---

# 9. Delivery Validation

Before recording a delivery, the ERP validates:

* Customer exists.
* Route exists.
* Delivery belongs to today's route.
* Delivery shift is valid.

For unplanned deliveries:

* Customer must already exist.
* Customer must belong to the same route.
* Reason must be provided.

Possible exceptions:

* DeliveryNotFoundError
* InvalidRouteError
* UnplannedDeliveryError

---

# 10. Token Validation

When registering token sheets, the ERP validates:

* Customer exists.
* Token Identity exists.
* Token Book is active.
* Sheet number is valid.
* Sheet has not already been used.
* Milk type matches the Token Identity.

Warnings include:

* Non-sequential sheet
* Previous book not completed
* Manual override

Possible exceptions:

* TokenBookNotFoundError
* DuplicateTokenSheetError
* InvalidTokenBookError
* InvalidMilkTypeError

---

# 11. Payment Validation

Before recording a payment, the ERP validates:

* Customer exists.
* Payment amount is valid.
* Outstanding balance exists.
* Payment mode is supported.

Possible exceptions:

* PaymentNotFoundError
* InvalidPaymentAmountError
* OutstandingBalanceNotFoundError

---

# 12. Reconciliation Validation

Before closing a route, the ERP verifies:

* Every delivery has been processed.
* Token registration is complete.
* Cash sales are entered.
* Returned milk is entered.
* Loaded milk equals:

```text id="vh001"
Token Milk

+

Cash Sales

+

Returned Milk
```

If reconciliation fails:

* Route remains open.
* Checker can edit the register.
* Reconciliation must succeed before closing.

Possible exceptions:

* RouteNotBalancedError
* MissingTokenRegistrationError

---

# 13. Exception Handling Strategy

Every exception follows a consistent structure.

Example:

```json
{
    "success": false,
    "message": "Customer not found.",
    "error_code": "CUSTOMER_NOT_FOUND"
}
```

The frontend can use the error code to display appropriate messages.

---

# 14. HTTP Status Codes

The ERP follows standard HTTP status codes.

| Status Code | Meaning               |
| ----------- | --------------------- |
| 200         | Request Successful    |
| 201         | Resource Created      |
| 400         | Bad Request           |
| 401         | Unauthorized          |
| 403         | Forbidden             |
| 404         | Resource Not Found    |
| 409         | Conflict              |
| 422         | Validation Failed     |
| 500         | Internal Server Error |

---

# 15. Custom Business Exceptions

The ERP defines custom exceptions for business operations.

Examples include:

### Customer Exceptions

* CustomerNotFoundError
* DuplicatePrimaryPhoneError
* SamePhoneNumberError

---

### Route Exceptions

* RouteNotFoundError
* DuplicateRouteCodeError
* InactiveRouteError

---

### Token Exceptions

* TokenBookNotFoundError
* DuplicateTokenSheetError
* InvalidTokenBookError

---

### Subscription Exceptions

* SubscriptionNotFoundError
* DuplicateSubscriptionError
* InactiveCustomerError
* InactiveMilkTypeError
* InvalidSubscriptionQuantityError
* SubscriptionAlreadyInactiveError

---

### Delivery Exception Exceptions

* DeliveryExceptionNotFoundError
* InactiveSubscriptionError
* InvalidDeliveryExceptionDateError
* DeliveryExceptionOverlapError
* DeliveryExceptionAlreadyInactiveError

---

### Payment Exceptions

* InvalidPaymentAmountError
* OutstandingBalanceNotFoundError

---

### Reconciliation Exceptions

* RouteNotBalancedError
* MissingTokenRegistrationError

---

### Authentication Exceptions

* InvalidCredentialsError
* InvalidTokenError
* ExpiredTokenError
* UnauthorizedAccessError

---

# 16. Error Logging

Unexpected system errors are automatically logged.

The log includes:

* Date
* Time
* User
* Module
* API Endpoint
* Error Type
* Stack Trace

These logs help developers diagnose and resolve issues without exposing technical details to users.

---

# 17. User-Friendly Error Messages

The ERP provides clear and meaningful messages.

Examples:

| Technical Exception        | User Message                                    |
| -------------------------- | ----------------------------------------------- |
| CustomerNotFoundError      | Customer not found.                             |
| DuplicatePrimaryPhoneError | Primary phone number already exists.            |
| RouteNotBalancedError      | Route reconciliation is not balanced.           |
| DuplicateTokenSheetError   | This token sheet has already been registered.   |
| InvalidTokenBookError      | The selected token book is inactive or invalid. |

The system avoids exposing internal implementation details.

---

# 18. Future Enhancements

Future improvements may include:

* Multi-language validation messages.
* Configurable business rules.
* Warning severity levels.
* Automatic correction suggestions.
* AI-assisted error diagnosis.
* Real-time frontend validation.
* Bulk validation for imports.

---

# 19. Conclusion

The Validation and Exception Handling module ensures that only accurate, consistent, and authorized data enters the Milk Distribution ERP. By combining input validation, business rule enforcement, database integrity checks, and structured exception handling, the system prevents invalid operations while maintaining data quality and providing meaningful feedback to users. This foundation improves reliability, simplifies maintenance, and supports the long-term scalability of the ERP.
