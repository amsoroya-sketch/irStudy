# PRD-WEEK1-003: Frontend Integration - Display 207 Personas

**Priority**: P0 (Critical)
**Estimated Time**: 3 hours
**Status**: Ready for Implementation
**Dependencies**: PRD-WEEK1-002 (Database Insertion)
**Blocks**: User testing, production launch

---

## Executive Summary

Update frontend UI to fetch and display all 207 personas from the database API, with filtering by specialty/difficulty and search functionality.

---

## Success Criteria

1. ✅ Persona selector dropdown shows all 207 personas
2. ✅ Filter by specialty (Cardiology, Emergency, GP, Pediatrics, Respiratory)
3. ✅ Filter by difficulty (Easy, Medium, Hard)
4. ✅ Search by name or diagnosis
5. ✅ Selected persona loads successfully
6. ✅ Zero frontend errors

---

## Technical Specification

### Files to Modify

**1. API Service** (`frontend/src/services/api.ts`):
```typescript
export interface PersonaListItem {
  id: number;
  persona_id: string;
  name: string;
  age: number;
  gender: string;
  specialty: string;
  diagnosis: string;
  difficulty: string;
}

export const getPersonas = async (params?: {
  specialty?: string;
  difficulty?: string;
  search?: string;
}): Promise<PersonaListItem[]> => {
  const response = await axiosInstance.get('/personas', { params });
  return response.data;
};

export const getPersonaDetail = async (personaId: string): Promise<any> => {
  const response = await axiosInstance.get(`/personas/${personaId}`);
  return response.data;
};
```

**2. OSCE Practice Page** (`frontend/src/pages/OSCEPractice.tsx`):
```typescript
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getPersonas, getPersonaDetail } from '../services/api';

export const OSCEPractice = () => {
  const [selectedSpecialty, setSelectedSpecialty] = useState<string>('');
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>('');
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [selectedPersonaId, setSelectedPersonaId] = useState<string>('');

  // Fetch persona list
  const { data: personas, isLoading } = useQuery({
    queryKey: ['personas', selectedSpecialty, selectedDifficulty, searchTerm],
    queryFn: () => getPersonas({
      specialty: selectedSpecialty || undefined,
      difficulty: selectedDifficulty || undefined,
      search: searchTerm || undefined
    })
  });

  // Fetch selected persona detail
  const { data: personaDetail } = useQuery({
    queryKey: ['persona-detail', selectedPersonaId],
    queryFn: () => getPersonaDetail(selectedPersonaId),
    enabled: !!selectedPersonaId
  });

  return (
    <div className="osce-practice">
      {/* Filters */}
      <div className="filters">
        <select
          value={selectedSpecialty}
          onChange={(e) => setSelectedSpecialty(e.target.value)}
        >
          <option value="">All Specialties</option>
          <option value="Cardiology">Cardiology</option>
          <option value="Emergency">Emergency</option>
          <option value="General Practice">General Practice</option>
          <option value="Pediatrics">Pediatrics</option>
          <option value="Respiratory">Respiratory</option>
        </select>

        <select
          value={selectedDifficulty}
          onChange={(e) => setSelectedDifficulty(e.target.value)}
        >
          <option value="">All Difficulties</option>
          <option value="Easy">Easy</option>
          <option value="Medium">Medium</option>
          <option value="Hard">Hard</option>
        </select>

        <input
          type="text"
          placeholder="Search by name or diagnosis..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      {/* Persona List */}
      <div className="persona-list">
        <label>Select Patient ({personas?.length || 0} available)</label>
        <select
          value={selectedPersonaId}
          onChange={(e) => setSelectedPersonaId(e.target.value)}
        >
          <option value="">-- Select a patient --</option>
          {personas?.map((p) => (
            <option key={p.persona_id} value={p.persona_id}>
              {p.name} - {p.diagnosis} ({p.difficulty})
            </option>
          ))}
        </select>
      </div>

      {/* Persona Detail */}
      {personaDetail && (
        <div className="persona-detail">
          <h2>{personaDetail.name}</h2>
          <p>Age: {personaDetail.age}, Gender: {personaDetail.gender}</p>
          <p>Chief Complaint: {personaDetail.chief_complaint}</p>
          {/* Render full persona details */}
        </div>
      )}
    </div>
  );
};
```

---

## Implementation Steps

1. Update API service with persona endpoints
2. Modify OSCE practice page with filters
3. Add loading states and error handling
4. Test with all 207 personas
5. Deploy to staging environment

---

## Acceptance Criteria

- [ ] All 207 personas visible in dropdown
- [ ] Filtering works correctly
- [ ] Search returns relevant results
- [ ] Persona detail loads without errors
- [ ] UI responsive (<100ms filter updates)

---

**Estimated Time**: 3 hours
**Status**: Ready for Ralph Loop Execution
