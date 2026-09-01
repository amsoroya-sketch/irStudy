# Defensive Coding Patterns for React Components

**Version**: 1.0
**Date**: 2026-05-27
**Applies to**: All React/TypeScript components in irStudy frontend

---

## ⚠️ CRITICAL: Unsafe Property Access Pattern

### Common Error: "Cannot read properties of undefined (reading 'X')"

This is the **most common runtime error** in React applications. It occurs when accessing properties or methods on potentially undefined/null values.

---

## 🔍 Anti-Patterns to Avoid

### ❌ UNSAFE: Direct property access without validation

```tsx
// BAD - Will crash if data is undefined or items is undefined
{!isLoading && !error && data && (
  <Grid container>
    {data.items.map((item) => (  // ❌ CRASH if data.items is undefined
      <Card key={item.id}>{item.name}</Card>
    ))}
  </Grid>
)}
```

### ❌ UNSAFE: Array spread without validation

```tsx
// BAD - Will crash if specialties is undefined
const sortedData = [...specialties].sort((a, b) => a.value - b.value);
```

### ❌ UNSAFE: Nested property chains

```tsx
// BAD - Multiple points of failure
const count = response.data.metrics.specialty_stats.length;
```

### ❌ UNSAFE: Map on potentially undefined arrays

```tsx
// BAD - Prop might be undefined
interface Props {
  trends: WeeklyTrend[];  // Not optional in type, but could be undefined at runtime
}

const PerformanceChart: React.FC<Props> = ({ trends }) => {
  const chartData = trends.map((trend) => ({  // ❌ CRASH if trends is undefined
    week: trend.week_start,
    value: trend.accuracy
  }));
};
```

---

## ✅ Safe Patterns to Use

### ✅ OPTION 1: Optional Chaining + Nullish Coalescing (Recommended)

```tsx
// GOOD - Safe with optional chaining
{!isLoading && !error && data?.items && (
  <Grid container>
    {data.items.map((item) => (
      <Card key={item.id}>{item.name}</Card>
    ))}
  </Grid>
)}

// GOOD - Default to empty array
const sortedData = [...(specialties ?? [])].sort((a, b) => a.value - b.value);

// GOOD - Nested safety
const count = response?.data?.metrics?.specialty_stats?.length ?? 0;
```

### ✅ OPTION 2: Array.isArray() Type Guard (Most Robust)

```tsx
// GOOD - Explicit type checking
{!isLoading && !error && Array.isArray(data?.items) && (
  <Grid container>
    {data.items.map((item) => (
      <Card key={item.id}>{item.name}</Card>
    ))}
  </Grid>
)}
```

### ✅ OPTION 3: Extract with Defaults (Best for Complex Components)

```tsx
// GOOD - Extract at top of component
const MyComponent: React.FC = () => {
  const { data, isLoading, error } = useQuery(...);

  // Extract with safe defaults
  const items = data?.items ?? [];
  const total = data?.total ?? 0;
  const metadata = data?.metadata ?? { count: 0, page: 1 };

  return (
    <>
      {!isLoading && !error && (
        <Grid container>
          {items.map((item) => (  // Safe - always an array
            <Card key={item.id}>{item.name}</Card>
          ))}
        </Grid>
      )}

      {total > 20 && (  // Safe - always a number
        <Pagination count={Math.ceil(total / 20)} />
      )}
    </>
  );
};
```

### ✅ OPTION 4: Props with Default Values (Child Components)

```tsx
// GOOD - Default props for arrays
interface Props {
  trends: WeeklyTrend[];
}

const PerformanceChart: React.FC<Props> = ({ trends = [] }) => {
  // Safe - trends is always an array (empty if undefined)
  const chartData = trends.map((trend) => ({
    week: trend.week_start,
    value: trend.accuracy
  }));

  return <LineChart data={chartData} />;
};
```

---

## 📋 Checklist: Before Using .map(), .filter(), .reduce()

Before calling array methods, ALWAYS verify:

- [ ] The parent object exists (`data &&` or `data?.`)
- [ ] The array property exists (`data.items &&` or `data?.items`)
- [ ] The array is actually an array (`Array.isArray(data?.items)`)
- [ ] OR use default empty array (`const items = data?.items ?? []`)

---

## 🎯 Quick Reference by Use Case

### Use Case: React Query Data

```tsx
const { data, isLoading, error } = useQuery(...);

// ✅ RECOMMENDED
const items = data?.items ?? [];
const total = data?.total ?? 0;

{!isLoading && !error && (
  <>
    {items.map(...)}
    <Pagination count={total} />
  </>
)}
```

### Use Case: Props Passed to Child Components

```tsx
// Parent
<ChildComponent items={data?.items ?? []} />

// Child - with default parameter
interface Props {
  items: Item[];
}

const ChildComponent: React.FC<Props> = ({ items = [] }) => {
  return <>{items.map(...)}</>;  // Safe
};
```

### Use Case: Nested API Responses

```tsx
// ❌ UNSAFE
const stats = apiResponse.data.metrics.specialty_breakdown.map(...);

// ✅ SAFE
const stats = apiResponse?.data?.metrics?.specialty_breakdown ?? [];
const chartData = stats.map(...);
```

### Use Case: Conditional Rendering

```tsx
// ❌ UNSAFE
{data.items.length > 0 && <List items={data.items} />}

// ✅ SAFE
{data?.items && data.items.length > 0 && <List items={data.items} />}

// ✅ EVEN BETTER
{(data?.items?.length ?? 0) > 0 && <List items={data.items} />}
```

---

## 🚨 Common Scenarios That Cause This Error

### Scenario 1: API Returns Different Shape Than Expected

```tsx
// Expected: { items: [...], total: 100 }
// Actual: { data: [...], count: 100 }  // Different property names

// ❌ CRASH
const items = response.items.map(...);

// ✅ SAFE - Handles unexpected response
const items = response?.items ?? response?.data ?? [];
```

### Scenario 2: Empty Response (204 No Content)

```tsx
// API returns: undefined (204 status)

// ❌ CRASH
const count = response.items.length;

// ✅ SAFE
const count = response?.items?.length ?? 0;
```

### Scenario 3: Race Conditions / Stale Data

```tsx
// Component unmounts before data arrives

// ❌ CRASH
useEffect(() => {
  fetchData().then(data => {
    setItems(data.items);  // Component might be unmounted
  });
}, []);

// ✅ SAFE
useEffect(() => {
  let cancelled = false;

  fetchData().then(data => {
    if (!cancelled && data?.items) {
      setItems(data.items);
    }
  });

  return () => { cancelled = true; };
}, []);
```

---

## 🔧 Auto-Fix Pattern (For Agents)

When you encounter this pattern in code:

```tsx
// BEFORE (Unsafe)
{data && data.items.map((item) => ...)}

// AFTER (Safe)
{data?.items && data.items.map((item) => ...)}

// OR BETTER
const items = data?.items ?? [];
{items.map((item) => ...)}
```

**Agent Auto-Fix Algorithm**:
1. Find all `.map(`, `.filter(`, `.reduce(`, `.length`, `.forEach(` calls
2. Trace back to the variable source
3. If from API/props/state, add optional chaining (`?.`)
4. If rendering, extract to variable with default value at component top

---

## 📚 TypeScript Integration

### Strict Null Checks

Ensure `tsconfig.json` has:

```json
{
  "compilerOptions": {
    "strict": true,
    "strictNullChecks": true,
    "noUncheckedIndexedAccess": true
  }
}
```

This makes TypeScript warn about potential undefined access **before runtime**.

### Type Guards

```tsx
function isArrayWithItems<T>(value: T[] | undefined): value is T[] {
  return Array.isArray(value) && value.length > 0;
}

// Usage
if (isArrayWithItems(data?.items)) {
  // TypeScript knows data.items is T[] here
  const mapped = data.items.map(...);
}
```

---

## 🎓 Training Examples

### Example 1: MCQBrowser (Original Error)

```tsx
// ❌ ORIGINAL (Line 186-189)
{!isLoading && !error && mcqsData && (
  <Grid container spacing={3}>
    {mcqsData.items.map((mcq) => (  // CRASH: items could be undefined
      <Grid size={{ xs: 12, sm: 6, md: 4 }} key={mcq.id}>
        <Card>...</Card>
      </Grid>
    ))}
  </Grid>
)}

// ✅ FIX OPTION 1: Add items check
{!isLoading && !error && mcqsData?.items && (
  <Grid container spacing={3}>
    {mcqsData.items.map((mcq) => (
      <Grid size={{ xs: 12, sm: 6, md: 4 }} key={mcq.id}>
        <Card>...</Card>
      </Grid>
    ))}
  </Grid>
)}

// ✅ FIX OPTION 2: Extract with default (RECOMMENDED)
const MCQBrowser: React.FC = () => {
  const { data: mcqsData, isLoading, error } = useQuery(...);

  const items = mcqsData?.items ?? [];
  const total = mcqsData?.total ?? 0;

  return (
    <Container>
      {!isLoading && !error && (
        <>
          <Grid container spacing={3}>
            {items.map((mcq) => (
              <Grid size={{ xs: 12, sm: 6, md: 4 }} key={mcq.id}>
                <Card>...</Card>
              </Grid>
            ))}
          </Grid>

          {total > 20 && (
            <Pagination count={Math.ceil(total / 20)} />
          )}

          {items.length === 0 && (
            <Typography>No MCQs found</Typography>
          )}
        </>
      )}
    </Container>
  );
};
```

### Example 2: Dashboard Metrics

```tsx
// ❌ ORIGINAL
const dashboardMetrics = emrData.metrics ? {
  specialty_breakdown: emrData.metrics.specialty_stats.map(stat => ({  // CRASH
    specialty: stat.specialty,
    session_count: stat.session_count,
  })),
} : undefined;

// ✅ FIXED
const dashboardMetrics = emrData?.metrics ? {
  specialty_breakdown: (emrData.metrics.specialty_stats ?? []).map(stat => ({
    specialty: stat.specialty,
    session_count: stat.session_count,
  })),
} : undefined;
```

---

## 🤖 Agent Instructions

When writing or reviewing React components:

1. **ALWAYS** extract array data with defaults at the top of components
2. **NEVER** directly `.map()` on API response properties
3. **USE** optional chaining (`?.`) for ALL API data access
4. **USE** nullish coalescing (`??`) to provide safe defaults
5. **VERIFY** prop types and provide default parameters for array props
6. **CHECK** that TypeScript `strictNullChecks` is enabled

### Pre-Commit Checklist

Before submitting code:
- [ ] All `.map()` calls have safety checks
- [ ] All API response properties use `?.` or have defaults
- [ ] All array props have default parameters
- [ ] Component has early return for loading/error states
- [ ] No direct nested property access (e.g., `data.a.b.c`)

---

## 📖 Further Reading

- [TypeScript Handbook: Narrowing](https://www.typescriptlang.org/docs/handbook/2/narrowing.html)
- [MDN: Optional Chaining](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Optional_chaining)
- [MDN: Nullish Coalescing](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Nullish_coalescing)

---

**Last Updated**: 2026-05-27
**Applies to**: irStudy Platform - All Frontend Components
