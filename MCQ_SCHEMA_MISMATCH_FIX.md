# MCQ Schema Mismatch - Root Cause & Fix

**Date**: 2026-05-27
**Issue**: MCQ Browser shows "No MCQs" despite 1,613 MCQs in database

---

## Root Cause

**Schema Mismatch** between frontend and backend:

### Backend (`/api/v1/mcqs/`)
Returns: **Flat array**
```python
@router.get("/", response_model=List[MCQPublic])
async def list_mcqs(...):
    mcqs = query.offset(skip).limit(min(limit, 100)).all()
    return mcqs  # Returns: [{mcq1}, {mcq2}, ...]
```

### Frontend (`getMCQs()`)
Expects: **Wrapped object with metadata**
```typescript
export interface MCQListResponse {
  items: MCQ[];
  total: number;
  skip: number;
  limit: number;
}

const response = await axiosInstance.get<MCQListResponse>('/mcqs', ...);
// Expects: {items: [...], total: 123, skip: 0, limit: 20}
```

---

## Impact

- Frontend code: `const items = mcqsData?.items ?? []`
- Backend returns: `[{mcq1}, {mcq2}...]`
- Frontend tries to access: `undefined.items`
- Result: Empty array, no MCQs displayed

---

## Fix Options

### Option 1: Update Backend (Recommended)
**Change backend to return paginated response**

**File**: `backend/src/api/v1/mcqs.py`

```python
# Add response model
class MCQListResponse(BaseModel):
    items: List[MCQPublic]
    total: int
    skip: int
    limit: int

# Update endpoint
@router.get("/", response_model=MCQListResponse)
async def list_mcqs(...):
    query = db.query(MCQ).filter(MCQ.is_published == True)

    # Apply filters...

    # Get total count BEFORE pagination
    total = query.count()

    # Apply pagination
    mcqs = query.offset(skip).limit(min(limit, 100)).all()

    # Return wrapped response
    return MCQListResponse(
        items=mcqs,
        total=total,
        skip=skip,
        limit=limit
    )
```

**Pros**:
- Proper pagination metadata
- Consistent with REST best practices
- Frontend code works as-is

**Cons**:
- Requires schema update
- Need to update schema file

---

### Option 2: Update Frontend (Alternative)
**Change frontend to handle flat array**

**File**: `frontend/src/api/mcqs.ts`

```typescript
export const getMCQs = async (params?: MCQListParams): Promise<MCQ[]> => {
  const response = await axiosInstance.get<MCQ[]>('/mcqs', {
    params: {...}
  });
  return response.data;  // Return flat array
};
```

**Then in MCQBrowser.tsx**:
```typescript
const { data: mcqsArray } = useQuery(...);
const items = mcqsArray ?? [];  // Use directly
```

**Pros**:
- Quick fix
- No backend changes

**Cons**:
- No pagination metadata (total count)
- Inconsistent with other API endpoints
- Can't show "Page X of Y"

---

### Option 3: Quick Workaround (Immediate)
**Transform response in frontend API client**

**File**: `frontend/src/api/mcqs.ts`

```typescript
export const getMCQs = async (params?: MCQListParams): Promise<MCQListResponse> => {
  const response = await axiosInstance.get<MCQ[]>('/mcqs', {
    params: {...}
  });

  // Transform flat array to expected format
  return {
    items: response.data,
    total: response.data.length,  // Approximation
    skip: params?.skip || 0,
    limit: params?.limit || 20,
  };
};
```

**Pros**:
- Works immediately
- No backend changes
- Frontend code unchanged

**Cons**:
- `total` is wrong (shows page count, not database count)
- Pagination broken

---

## Recommended Solution

**Implement Option 1** (Update Backend)

1. Add `MCQListResponse` schema
2. Update endpoint to return wrapped response
3. Run backend tests
4. Frontend works without changes

**Time**: 10 minutes

---

## Additional Issues Found

While investigating, also discovered:
- OSCE import blocked (enum mismatch - separate issue)
- Some frontend components using deprecated `MCQListResponse` type

---

**Status**: Root cause identified
**Next Step**: Choose fix option and implement
