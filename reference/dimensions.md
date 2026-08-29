# Quality Dimensions

20 dimensions for subjective code quality review. Each has a description, what to look for, and what to skip.

---

## naming_quality
Function/variable/file names that communicate intent.

**Look for:**
- Generic verbs that reveal nothing: process, handle, do, run, manage
- Name/behavior mismatch: getX() that mutates state, isX() returning non-boolean
- Vocabulary divergence from codebase norms (context provides the norms)
- Abbreviations inconsistent with codebase conventions

**Skip:**
- Standard framework names (render, mount, useEffect)
- Short-lived loop variables (i, j, k)
- Well-known abbreviations matching codebase convention (ctx, req, res)
- Short names that are established project conventions used consistently — a name used 50+ times is a convention, not an outlier

---

## logic_clarity
Control flow and logic that provably does what it claims.

**Look for:**
- Identical if/else or ternary branches (same code on both sides)
- Dead code paths: code after unconditional return/raise/throw/break
- Always-true or always-false conditions (e.g. checking a constant)
- Redundant null/undefined checks on values that cannot be null
- Async functions that never await (synchronous wrapped in async)
- Boolean expressions that simplify: `if x: return True else: return False`

**Skip:**
- Deliberate no-op branches with explanatory comments
- Framework lifecycle methods that must be async by contract
- Guard clauses that are defensive by design

---

## type_safety
Type annotations that match runtime behavior.

**Look for:**
- Return type annotations that don't cover all code paths (e.g., -> str but can return None)
- Parameters typed as X but called with Y (e.g., str param receiving None)
- Union types that could be narrowed (Optional used where None is never valid)
- Missing annotations on public API functions
- Type: ignore comments without explanation
- TypedDict fields marked Required but accessed via .get() with defaults — the type promises a shape the code doesn't trust
- Parameters typed as dict[str, Any] where a specific TypedDict or dataclass exists
- Enum types defined in the codebase but bypassed with raw string or int literal comparisons
- Parallel type definitions: a Literal alias that duplicates an existing enum's values

**Skip:**
- Untyped private helpers in well-typed modules
- Dynamic framework code where typing is impractical
- Test code with loose typing

---

## contract_coherence
Functions and modules that honor their stated contracts.

**Look for:**
- Return type annotation lies: declared type doesn't match all return paths
- Docstring/signature divergence: params described in docs but not in function signature
- Functions named getX that mutate state (side effect hidden behind getter name)
- Module-level API inconsistency: some exports follow a pattern, one doesn't
- Error contracts: function says it throws but silently returns None, or vice versa

**Skip:**
- Protocol/interface stubs (abstract methods with placeholder returns)
- Test helpers where loose typing is intentional
- Overloaded functions with multiple valid return types

---

## error_consistency
Consistent error strategies, preserved context, predictable failure modes.

**Look for:**
- Mixed error strategies: some functions throw, others return null, others use Result types
- Error context lost at boundaries: catch-and-rethrow without wrapping original
- Inconsistent error types: custom error classes in some modules, bare strings in others
- Silent error swallowing: catches that log but don't propagate or recover
- Missing error handling on I/O boundaries (file, network, parse operations)

**Skip:**
- Intentional error boundaries at top-level handlers
- Different strategies for different layers (e.g. Result in core, throw in CLI)

---

## abstraction_fitness
Abstractions that pay for themselves with real leverage.

**Look for:**
- Pass-through wrappers or interfaces that add no behavior, policy, or translation
- Cross-cutting wrapper chains where call depth increases without added value
- Interface/protocol families where most declared contracts have only one implementation
- Systemic util/helper dumping grounds that create low cohesion across modules
- Leaky abstractions: callers consistently bypass intended interfaces
- Wide options/context bag APIs that hide true domain boundaries
- Generic/type-parameter machinery used in only one concrete way
- Delegation-heavy classes where most methods forward to an inner object
- Facade/re-export modules that define no logic of their own
- Getter functions whose body is solely return x.get(key) — the underlying type should be an object with properties

**Skip:**
- Dependency-injection or framework abstractions required for wiring/testability (if a seam exists solely so tests can mock, report under test_strategy)
- Adapters that intentionally isolate external API volatility
- Cases where abstraction clearly reduces duplication across multiple callers
- Thin wrappers that consistently enforce policy (auth/logging/metrics/caching)
- If the core issue is dependency direction or cycles, use cross_module_architecture

---

## ai_generated_debt
LLM-hallmark patterns: restating comments, defensive overengineering, boilerplate.

**Look for:**
- Restating comments that echo the code without adding insight (// increment counter above i++)
- Nosy debug logging: entry/exit logs on every function, full object dumps to console
- Defensive overengineering: null checks on non-nullable typed values, try-catch around pure expressions
- Docstring bloat: multi-line docstrings on trivial 2-line functions
- Pass-through wrapper functions with no added logic (just forward args to another function)
- Generic names in domain code: handleData, processItem, doOperation where domain terms exist
- Identical boilerplate error handling copied verbatim across multiple files
- Fictitious edge cases: branches for states unreachable from any call site, fallbacks for configurations that can't exist
- Redundant timeouts at multiple layers of a call path when a single timeout at the boundary that owns the deadline would cover it
- Additive patching: layers that compensate for a bad upstream premise instead of deleting it — V2 functions living beside their V1, flags that disable earlier behavior, transforms that fix up another layer's output

**Skip:**
- Comments explaining WHY (business rules, non-obvious constraints, external dependencies)
- Defensive checks at genuine API boundaries (user input, network, file I/O)
- Generated code (protobuf, GraphQL codegen, ORM migrations)
- Wrapper functions that add auth, logging, metrics, or caching
- A single deliberate timeout at the boundary that owns the deadline, or timeouts a library API requires
- Old/new coexistence that is an active tracked migration or backward-compat need — report under incomplete_migration

---

## high_level_elegance
Clear decomposition, coherent ownership, domain-aligned structure.

**Look for:**
- Top-level packages/files map to domain capabilities rather than historical accidents
- Ownership and change boundaries are predictable — a new engineer can explain why this exists
- Public surface (exports/entry points) is small and consistent with stated responsibility
- Project contracts and reference docs match runtime reality (README/structure/philosophy are trustworthy)
- Subsystem decomposition localizes change without surprising ripple edits
- Subsystem responsibilities are disjoint — no two subsystems each partially own the same concern, leaving it unclear which one to change
- A small set of architectural patterns is used consistently across major areas

**Skip:**
- When dependency direction/cycle/hub failures are the PRIMARY issue, report under cross_module_architecture
- When handoff mechanics are the PRIMARY issue, report under mid_level_elegance
- When function/class internals are the PRIMARY issue, report under low_level_elegance or logic_clarity
- Pure naming/style nits with no impact on role clarity

---

## mid_level_elegance
Quality of handoffs and integration seams across modules and layers.

**Look for:**
- Inputs/outputs across boundaries are explicit, minimal, and unsurprising
- Data translation at boundaries happens in one obvious place
- Error and lifecycle propagation across boundaries follows predictable patterns
- Orchestration reads as composition of collaborators, not tangled back-and-forth calls
- Integration seams avoid glue-code entropy (ad-hoc mappers and boundary conditionals)
- Problems are solved at the layer that owns the cause, not patched where the symptom surfaces (e.g. retry logic in the UI, input validation deferred to the storage adapter)

**Skip:**
- When top-level decomposition/package shape is the PRIMARY issue, report under high_level_elegance
- When implementation craft inside one function/class is the PRIMARY issue, report under low_level_elegance
- Pure API/type contract defects with no seam design impact (belongs to contract_coherence)
- Standalone naming/style preferences that do not affect handoffs

---

## low_level_elegance
Direct, precise function and class internals.

**Look for:**
- Control flow is direct and intention-revealing; branches are necessary and distinct
- State mutation and side effects are explicit, local, and bounded
- Edge-case handling is precise without defensive sprawl
- Extraction level is balanced: avoids both monoliths and micro-fragmentation
- Helper extraction style is consistent across related modules

**Skip:**
- When file responsibility/package role is the PRIMARY issue, report under high_level_elegance
- When inter-module seam choreography is the PRIMARY issue, report under mid_level_elegance
- When dependency topology is the PRIMARY issue, report under cross_module_architecture
- Provable logic/type/error defects already captured by logic_clarity, type_safety, or error_consistency

---

## cross_module_architecture
Dependency direction, cycles, hub modules, and boundary integrity.

**Look for:**
- Layer/dependency direction violations repeated across multiple modules
- Cycles or hub modules that create large blast radius for common changes
- Documented architecture contracts drifting from runtime (e.g. dynamic import boundaries)
- Cross-module coordination through shared mutable state or import-time side effects
- Compatibility shim paths that persist without active external need and blur boundaries
- Cross-package duplication that indicates a missing shared boundary
- Duplicate sources of truth: the same state or config maintained in two places, with machinery invented to keep them synchronized
- Subsystem or package consuming a disproportionate share of the codebase

**Skip:**
- Intentional facades/re-exports with clear API purpose
- Framework-required patterns (Django settings, plugin registries)
- Package naming/placement tidy-ups without boundary harm (belongs to package_organization)
- Local readability/craft issues (belongs to low_level_elegance)

---

## initialization_coupling
Boot-order dependencies, import-time side effects, global singletons.

**Look for:**
- Module-level code that depends on another module having been imported first
- Import-time side effects: DB connections, file I/O, network calls at module scope
- Global singletons where creation order matters across modules
- Environment variable reads at import time (fragile in testing)
- Circular init dependencies hidden behind conditional or lazy imports
- Module-level constants computed at import time alongside a dynamic getter function — consumers referencing the stale snapshot instead of calling the getter

**Skip:**
- Standard library initialization (logging.basicConfig)
- Framework bootstrap (app.configure, server.listen)

---

## convention_outlier
Naming convention drift, inconsistent file organization, style islands.

**Look for:**
- Naming convention drift: snake_case functions in a camelCase codebase or vice versa
- Inconsistent file organization that impedes navigation
- Mixed export patterns across sibling modules (named vs default, class vs function)
- Style islands: one directory uses a completely different pattern than the rest
- Sibling modules following different behavioral protocols
- Inconsistent plugin organization: sibling plugins structured differently
- Large __init__.py re-export surfaces that obscure internal module structure
- Mixed type strategies for domain objects (TypedDict for some, dataclass for others) without documented rationale

**Skip:**
- Intentional variation for different module types (config vs logic)
- Third-party code or generated files following their own conventions
- Do NOT recommend adding index/barrel files, re-export facades, or directory wrappers to "standardize"
- When sibling modules use different structures, report the inconsistency but do NOT suggest adding abstraction layers to unify them

---

## dependency_health
Unused deps, version conflicts, multiple libs for same purpose, heavy deps.

**Look for:**
- Multiple libraries for the same purpose (e.g. moment + dayjs, axios + fetch wrapper)
- Heavy dependencies pulled in for light use (e.g. lodash for one function)
- Circular dependency cycles visible in the import graph
- Unused dependencies in package.json/requirements.txt
- Version conflicts or pinning issues visible in lock files

**Skip:**
- Dev dependencies (test, build, lint tools)
- Peer dependencies required by frameworks

---

## test_strategy
Untested critical paths, coupling, snapshot overuse, fragility patterns.

**Look for:**
- Critical paths with zero test coverage (high-importer files, core business logic)
- Test-production coupling: tests that break when implementation details change
- Snapshot test overuse: >50% of tests are snapshot-based
- Missing integration tests: unit tests exist but no cross-module verification
- Test fragility: tests that depend on timing, ordering, or external state
- Production code that exists purely to satisfy tests: `if TESTING` branches, test-only hooks or exports, injection seams used only by mocks

**Skip:**
- Low-value files intentionally untested (types, constants, index files)
- Generated code that shouldn't have custom tests

---

## api_surface_coherence
Inconsistent API shapes, mixed sync/async, overloaded interfaces.

**Look for:**
- Inconsistent API shapes: similar functions with different parameter ordering or naming
- Mixed sync/async in the same module's public API
- Overloaded interfaces: one function doing too many things based on argument types
- Missing error contracts: no documentation or types indicating what can fail
- Public functions with >5 parameters (API boundary may be wrong)

**Skip:**
- Internal/private APIs where flexibility is acceptable
- Framework-imposed patterns (React hooks must follow rules of hooks)

---

## authorization_consistency
Auth/permission patterns consistently applied across the codebase.

**Look for:**
- Route handlers with auth decorators/middleware on some siblings but not others
- RLS enabled on some tables but not siblings in the same domain
- Permission strings as magic literals instead of shared constants
- Mixed trust boundaries: some endpoints validate user input, siblings don't
- Service role / admin bypass without audit logging or access control

**Skip:**
- Public routes explicitly documented as unauthenticated (health checks, login, webhooks)
- Internal service-to-service calls behind network-level auth
- Dev/test endpoints behind feature flags or environment checks

---

## incomplete_migration
Old+new API coexistence, deprecated-but-called symbols, stale migration shims.

**Look for:**
- Old and new API patterns coexisting: class+functional components, axios+fetch, moment+dayjs
- Deprecated symbols still called by active code (@deprecated, DEPRECATED markers)
- Compatibility shims that no caller actually needs anymore
- Mixed JS/TS files for the same module (incomplete TypeScript migration)
- Stale migration TODOs: TODO/FIXME referencing "migrate", "legacy", "old api", "remove after"

**Skip:**
- Active, intentional migrations with tracked progress
- Backward-compatibility for external consumers (published APIs, libraries)
- Gradual rollouts behind feature flags with clear ownership

---

## package_organization
Directory layout quality and navigability.

**Look for:**
- Straggler roots: root-level files with low fan-in (<5 importers) that share concern with other files should move under a focused package
- Import-affinity mismatch: file imports/references are mostly from one sibling domain (>60%), but file lives outside that domain
- Coupling-direction failures: reciprocal/bidirectional directory edges or obvious downstream-to-upstream imports
- Flat directory overload: >10 files with mixed concerns and low cohesion should be split into purpose-driven subfolders
- Ambiguous folder naming: directory names do not reflect contained responsibilities

**Skip:**
- Root-level files that ARE genuinely core — high fan-in (>=5 importers), imported across multiple subdirectories
- Small projects (<20 files) where flat structure is appropriate
- Framework-imposed directory layouts (src/, lib/, dist/, __pycache__/)
- Test directories mirroring production structure
- Aesthetic preferences without measurable navigation, ownership, or coupling impact

---

## design_coherence
Are structural design decisions sound — functions focused, abstractions earned, patterns consistent?

**Look for:**
- Functions doing too many things — multiple distinct responsibilities in one body
- Parameter lists that should be config/context objects — many related params passed together
- Files accumulating issues across many dimensions — likely mixing unrelated concerns
- Deep nesting that could be flattened with early returns or extraction
- Derived values stored alongside their source and manually kept in sync, instead of computed on demand
- Repeated structural patterns that should be data-driven

**Skip:**
- Functions that are long but have a single coherent responsibility
- Parameter lists where grouping would obscure meaning — do NOT recommend config/context objects or dependency injection wrappers just to reduce parameter count; only group when the grouping has independent semantic meaning
- Files that are large because their domain is genuinely complex, not because they mix concerns
- Nesting that is inherent to the problem (e.g., recursive tree processing)
- Deliberate performance caches or denormalization with a clear invalidation strategy
- Do NOT recommend extracting callable parameters or injecting dependencies for "testability" — direct function calls are simpler and preferred unless there is a concrete decoupling need
