---
title: Agentic Coding with EF Core and SQL Server
tags:
  - ai-agents
  - software-architecture
  - dotnet
  - sql-server
  - entity-framework
  - testing
  - database
  - llm-agents
aliases:
  - EF Core with AI Agents
  - SQL Server and Agentic Coding
---

# Agentic Coding with EF Core and SQL Server

## Thesis

Coding agents change the economics of choosing between EF Core, handwritten SQL, and database-side code.

Historically, handwritten SQL, result DTOs, mappers, stored procedures, and their tests created enough repetitive work that teams often preferred an ORM even when direct SQL would provide better control. An agent can generate and update much of this mechanical code cheaply. This makes a SQL-heavy approach more practical, but it does not make it automatically safer or architecturally superior.

The main question is no longer whether an agent can write SQL and map a result set to C# objects. It can. The important questions are:

- What is the source of truth?
- How is schema compatibility verified?
- Where should business logic live?
- How do we verify semantics, concurrency, and performance?
- Can humans still understand and review the resulting system?

## An Agent Can Easily Generate the Mapping Layer

Given a schema and a query, an agent can generate:

1. parameterized SQL;
2. command execution code;
3. a result DTO or record;
4. `DbDataReader` mapping or Dapper integration;
5. integration and contract tests.

Repetitive mapping code is not difficult for an agent. In fact, agents are less discouraged than humans by mechanical code. This reduces the cost of explicit implementations, but generated code still needs deterministic verification.

## The Real Problem Is Contract Consistency

A database read usually involves several representations that must agree:

| Layer | Example |
| --- | --- |
| Database schema | `Users.CreatedAt datetime2 NOT NULL` |
| SQL projection | `SELECT u.CreatedAt AS CreatedAt` |
| Data reader or mapper | `GetDateTime(...)` |
| C# result model | `DateTime CreatedAt` |

Potential mismatches include:

- `int` versus `bigint`;
- `decimal` versus `double`;
- `DateTime` versus `DateTimeOffset`;
- nullable versus non-nullable values;
- incorrect column aliases or order;
- unexpected nullability introduced by an outer join;
- provider-specific conversions;
- a structurally valid but semantically incorrect join.

These are often subtle errors: the code looks plausible and may survive superficial review.

## What Should Be the Source of Truth?

For persistence models, the natural direction is:

```text
Migrations → actual database schema → C# mapping
```

For query result models, the complete direction is:

```text
Migrations → actual schema → SQL query → result-set metadata → C# result type
```

A schema dump is useful but insufficient. A query result may include joins, aggregates, expressions, window functions, and nullability introduced by the query itself. The object often represents a use-case-specific projection rather than a table row.

Migrations should therefore remain the authoritative history. A generated schema snapshot can help agents, reviewers, documentation, and environment comparisons, but it should not become a separately edited source of truth.

## Discovering SQL-to-Type Dependencies

Comments such as `// Maps GetUserSummaries.sql` are useful to humans but too weak as the primary mechanism. They are not compiler-checked and can become stale.

A stronger option is an explicit attribute:

```csharp
[SqlResult("Users/GetUserSummaries.sql")]
public sealed record UserSummaryRow(
    long Id,
    string Email,
    int OrderCount,
    DateTime? LastOrderAt);
```

An even more structural option is a common query abstraction:

```csharp
public sealed class GetUserSummaries : SqlQuery<UserSummaryRow>
{
    public override string Sql => """
        SELECT ...
        """;
}
```

The attribute or abstraction is only valuable if an analyzer, source generator, or test reads it and performs real verification. The annotation itself does not guarantee correctness.

For many systems, checking all registered queries after every migration is simpler and safer than attempting sophisticated impact analysis. Dependency indexing can be added later if validation becomes too slow.

## Contract Tests Against a Real Migrated Database

EF Core also fails when the database changes without a corresponding mapping change. An ORM does not eliminate schema drift; it only changes where and how it appears. Therefore, both EF and handwritten SQL require tests against a database created from the real migrations.

A useful CI pipeline is:

```text
Create an empty database
→ apply every migration
→ validate EF mappings
→ validate every registered SQL query and result type
→ run integration tests
```

The contract validator should compare:

| Property | Verification |
| --- | --- |
| Column count | SQL result versus DTO properties or constructor |
| Name | SQL alias versus C# property |
| Type | SQL Server type versus CLR type |
| Nullability | Result nullability versus nullable C# type |
| Order | Required when positional mapping is used |
| Conversion | Only explicitly allowed conversions |

For SQL Server, result metadata can be inspected using facilities such as `sp_describe_first_result_set`. A provider-independent alternative is executing the command in a schema-only mode and inspecting `DbDataReader.GetColumnSchema()`, although provider behavior and nullability reporting must be verified.

The test suite should include at least:

1. rebuilding a database from all migrations;
2. upgrading a database from the currently deployed version, including representative existing data;
3. validating EF mappings;
4. validating SQL-to-DTO contracts;
5. testing important write/read round trips;
6. testing business semantics with representative data;
7. exercising critical end-to-end paths.

Contract tests detect structural incompatibility. They cannot detect that two fields with the same type were accidentally exchanged, or that a valid `INNER JOIN` removed required rows. Behavioral tests remain necessary.

## What Explicit SQL Provides

Handwritten SQL gives direct access to the capabilities of SQL Server rather than only the subset naturally expressible and translated through LINQ. This includes, among other things:

- window functions;
- recursive CTEs;
- `APPLY`;
- table-valued parameters;
- `OUTPUT`;
- temporal tables;
- JSON and full-text features;
- set-based bulk operations;
- inline table-valued functions;
- indexed views;
- exact transaction and isolation behavior;
- direct control over the executed statement.

The executed query is visible and can be copied into SSMS, measured, and inspected using actual execution plans, IO statistics, and timing data.

EF Core does not necessarily produce bad SQL. For ordinary filtering, projection, pagination, joins, and CRUD, it often produces perfectly adequate queries. Its limitations become more visible with complex graphs, multiple includes, complicated aggregation, provider-specific features, or queries whose translated shape is difficult to predict.

The distinction is therefore not simply “good SQL versus bad EF.” EF provides type information, convenient change tracking, refactoring support, and a discoverable model. Explicit SQL provides precise control and access to the database's full language.

## Moving Code into the Database

Agents also reduce the implementation cost of views, functions, and stored procedures. These mechanisms have different appropriate roles:

| Mechanism | Suitable use |
| --- | --- |
| View | Stable shared projection |
| Inline table-valued function | Parameterized, composable query |
| Stored procedure | Atomic command, batch operation, or stable read contract |
| Scalar function | Small deterministic calculation, used carefully |
| SQL file owned by the application | Query specific to one use case |

Good candidates for database-side implementation are operations that:

- are strongly set-oriented;
- process much data but return a small result;
- need SQL Server-specific features;
- benefit from a single round trip;
- must update multiple objects atomically;
- are performance-critical;
- represent a stable data-access contract.

Poor candidates include:

- orchestration across external systems;
- queues, retries, and long-running workflows;
- frequently changing business decisions;
- behavior that is difficult to observe and test in the database;
- logic moved merely because SQL can express it.

Otherwise the system develops two backends: one in C# and another hidden in stored procedures. An agent can cheaply add code to both, but reviewers and maintainers must still understand both.

## What Agents Reduce—and What They Do Not

Agents substantially reduce the cost of:

- writing SQL and DTOs;
- generating mappers;
- updating mechanical mappings after migrations;
- creating procedures and functions;
- generating representative test data;
- writing contract and integration test scaffolding;
- finding references to changed tables and columns;
- documenting query contracts;
- performing an initial analysis of execution plans.

They reduce much less of the cost of:

- validating business meaning;
- selecting architectural boundaries;
- reasoning about locks, isolation, and concurrency;
- safely migrating production data;
- judging whether an optimization works on real data;
- preserving institutional knowledge;
- reviewing a large body of clever SQL.

Cheap generation can even increase risk by making it easy to create more complex database code than the team can realistically review.

## A Practical Hybrid Architecture

A pragmatic .NET and SQL Server architecture could use:

- EF Core for ordinary writes, change tracking, relationships, and straightforward CRUD;
- explicit SQL or Dapper for use-case-specific read models;
- stored procedures for justified atomic or high-volume operations;
- views and inline table-valued functions for carefully selected shared projections;
- migrations as the only mechanism for changing tables, views, functions, and procedures;
- generated schema snapshots as agent and reviewer context;
- automatic SQL-to-DTO contract validation after every migration;
- integration tests for query semantics and important commands;
- measured execution plans for performance-critical queries.

A useful policy is:

> Start with the simplest representation appropriate to the operation. Move to explicit SQL, a view, a function, or a procedure when it provides a concrete benefit in performance, atomicity, composability, or access to SQL Server features.

## Guidance for Coding Agents

An agent working in this architecture should be instructed to:

1. inspect migrations and the generated schema snapshot before changing database code;
2. identify all affected queries, mappings, functions, views, and procedures;
3. use parameters rather than string interpolation;
4. avoid `SELECT *` in application contracts;
5. make aliases and nullability explicit;
6. create or update contract tests with every SQL result change;
7. add semantic tests for changed joins, filters, aggregation, and mutations;
8. run migrations and database integration tests locally;
9. measure rather than merely claim performance improvements;
10. keep business reasoning in the application unless database placement is explicitly justified.

## Conclusion

Agentic coding makes explicit SQL and database-side programming economically more attractive because it lowers the cost of repetitive implementation and maintenance. It does not remove the need for strong contracts, migrated-database tests, semantic review, or architectural discipline.

The likely outcome is not a return to putting the entire application in stored procedures. It is a more balanced architecture in which teams are less afraid of handwritten SQL, use SQL Server's strengths deliberately, and rely on deterministic validation rather than trusting either the ORM or the agent.

## Related Notes

- [[Designing Software Architecture with LLM Assistance]]
- [[LLM Coding Agents Reliability]]
- [[Agentic Coding Harness and Controlled Development Workflows|Agentic Harnesses for Software Development]]
- [[Testing in the Model, Agent, LLM Era|Testing as Executable Documentation]]
---

## Relationship to the Knowledge Graph

- **[[Designing Software for AI Agents]]**: Exposing structured, predictable database schemas and query boundaries to coding agents.
- **[[Refactoring Legacy Systems with AI Agents]]**: Modernizing database access layers and isolating legacy SQL queries.
- **[[Software Entropy and the Zero-Friction Trap]]**: Avoiding bloated entity relationships and leaky ORM abstractions generated by AI.
- **[[Designing Internal NuGet Packages as an Explicit, Composable Framework]]**: Encapsulating database access and repository patterns into explicit packages.
- **[[Why Business Logic Is the Hardest Part of Agentic Coding]]**: Isolating persistence logic from domain business rules.
