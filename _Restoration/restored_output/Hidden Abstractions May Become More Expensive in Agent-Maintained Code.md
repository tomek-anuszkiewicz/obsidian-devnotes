Syntactic brevity often hides massive execution pipelines. 
Consider this common MediatR call:

```csharp
public Task<Response> GetOrder(GetOrderRequest request) => mediator.Send(request);
```

The call site hides the true execution flow:

```text
Auth -> Validation -> Logging -> Transaction -> EF Interceptors -> Handler -> SQL
```

Local code stays small. Semantic complexity explodes.
Coding agents struggle with this hidden execution context.

### Non-Local Semantics and Ambient State

Agents cannot infer dependencies outside the local context window.
Consider an HTTP call:

```csharp
await httpClient.SendAsync(request);
```

Global handlers inject headers, auth, telemetry, and retries silently.
Entity Framework query filters also inject hidden SQL clauses:

```csharp
context.Orders.ToListAsync();
// Injects: WHERE TenantId = @currentTenant AND IsDeleted = 0
```

Do not hide business dependencies in ambient state.
Avoid `AsyncLocal`, `HttpContext.Items`, or implicit thread-local state.
Pass required context explicitly.

### Dynamic DI Breaks Static Analysis

Dynamic DI and runtime factories break static analysis tools.

```csharp
services.AddScoped<IPriceCalculator>(sp => {
    var context = sp.GetRequiredService<OperationContext>();
    return context.Channel switch
    {
        Channel.Web => new WebPriceCalculator(),
        Channel.Api => new ApiPriceCalculator(),
        _ => new DefaultPriceCalculator()
    };
});
```

The call site obscures the concrete implementation:

```csharp
priceCalculator.Calculate(order);
```

Keyed services, decorators, and assembly scanning destroy call-site discoverability.
Agents fail to identify the active execution path.
Interceptors also hide critical business semantics:

```csharp
repository.Save(order); // Silently runs auth, validation, and audit logging
```

Keep business-critical operations visible at the call site.

### The Shift in DRY Economics

Traditional DRY minimizes typing and repeated lines.
Agents generate and maintain repeated code cheaply.
Prioritize semantic locality over extreme deduplication.
Allow repeated code to keep pipelines explicit.

### Explicit Execution Pipelines

Expose the execution pipeline directly in the handler:

```csharp
return Operation
    .From(request)
    .Validate<GetOrderValidator>()
    .Authorize<ReadOrderPolicy>()
    .Retry(ExternalPolicies.Read)
    .Execute<GetOrderHandler>()
    .ValidateResponse<GetOrderResponseValidator>()
    .MapErrors<OrderHttpErrors>()
    .Return();
```

This code exposes the full execution graph.
Agents parse this pipeline without inspecting external framework configurations.

### Mechanics vs. Business Semantics

Let frameworks hide low-level mechanics.
Keep domain semantics explicit.

Safe to hide (Mechanics):
- JSON parsing, serializing, TCP handling
- Low-level telemetry, correlation IDs, compression

Keep explicit (Semantics):
- Authorization and tenant filtering
- Business validation and retry policies
- Transaction bounds and idempotency keys
- Cache invalidation and feature flags

### Named Semantics Over Silent Policies

Do not hide retries inside `HttpClient`.
Expose the retry policy at the call site:

```csharp
await request
    .Retry(RetryPolicies.ExternalRead)
    .Execute();
```

The call site declares *what* policy applies.
Central configuration defines *how* the policy executes.
Agents immediately recognize that the call may run multiple times.
They then handle idempotency and side effects correctly.

### Ubiquitous Vocabulary

Encode domain conclusions directly into code.
Avoid technical sentinels.

Bad:
```csharp
if (payment != null) // Implicitly means unpaid
if (amount == 0)     // Implicitly means free
if (status == 2)     // Implicitly means active
```

Good:
```csharp
if (payment.IsUnpaid)
if (price.IsFree)
if (subscription.IsActive)
```

Align naming across schemas, API contracts, tests, and code:
- Spec: `paymentStatus: "unpaid"`
- DB: `payment_status = "unpaid"`
- Code: `PaymentStatus.Unpaid`
- Test: `ShouldRetryUnpaidPayment()`

Consistent terminology improves agent retrieval and code reasoning.

### Semantic Locality Spectrum

Measure code quality by semantic locality:

- **High Locality:** 
```csharp
CalculatePrice(order, customer, pricingRules);
```
- **Medium Locality:** 
```csharp
priceCalculator.Calculate(order);
```
- **Low Locality:** Ambient DI resolves implementations via runtime tenant and flags.

Syntactic brevity no longer equals architectural simplicity.
Prioritize explicit, composable, and mechanically discoverable pipelines.
