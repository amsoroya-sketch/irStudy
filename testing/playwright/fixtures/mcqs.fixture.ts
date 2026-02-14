/**
 * MCQ Test Fixtures
 * Sample MCQ data for testing
 */

export interface MCQFixture {
  id: number;
  question: string;
  option_a: string;
  option_b: string;
  option_c: string;
  option_d: string;
  option_e: string;
  correct_answer: 'A' | 'B' | 'C' | 'D' | 'E';
  explanation: string;
  category: string;
  difficulty: 'easy' | 'medium' | 'hard';
  tags: string[];
  image_url?: string;
  citation?: string;
  created_at: string;
  updated_at: string;
}

/**
 * Sample MCQs for Cardiology category
 */
export const CARDIOLOGY_MCQS: MCQFixture[] = [
  {
    id: 1,
    question: 'A 55-year-old man presents with severe chest pain radiating to his left arm. What is the most appropriate initial management?',
    option_a: 'Aspirin 300mg chewed immediately',
    option_b: 'Ibuprofen 400mg orally',
    option_c: 'Paracetamol 1g orally',
    option_d: 'Wait for ECG results',
    option_e: 'Order chest X-ray first',
    correct_answer: 'A',
    explanation: 'Aspirin should be given immediately in suspected acute coronary syndrome to inhibit platelet aggregation. This is a time-critical intervention that should not be delayed for investigations.',
    category: 'Cardiology',
    difficulty: 'medium',
    tags: ['Acute', 'Cardiology', 'Emergency', 'AMC'],
    citation: 'AMC Clinical Examination, 8th Edition, Chapter 12: Cardiovascular System',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
  {
    id: 2,
    question: 'What is the most common cause of atrial fibrillation?',
    option_a: 'Ischaemic heart disease',
    option_b: 'Hypertension',
    option_c: 'Thyrotoxicosis',
    option_d: 'Mitral stenosis',
    option_e: 'Alcohol excess',
    correct_answer: 'B',
    explanation: 'Hypertension is the most common cause of atrial fibrillation globally, accounting for approximately 30% of cases. It causes left atrial enlargement and structural remodelling.',
    category: 'Cardiology',
    difficulty: 'easy',
    tags: ['Cardiology', 'Arrhythmia', 'AMC'],
    citation: 'Talley & O\'Connor Clinical Examination, 8th Edition, p.234',
    created_at: '2024-01-02T00:00:00Z',
    updated_at: '2024-01-02T00:00:00Z',
  },
];

/**
 * Sample MCQs for Respiratory category
 */
export const RESPIRATORY_MCQS: MCQFixture[] = [
  {
    id: 3,
    question: 'A 45-year-old smoker presents with progressive dyspnoea. Spirometry shows FEV1/FVC <0.7. What is the most likely diagnosis?',
    option_a: 'Asthma',
    option_b: 'COPD',
    option_c: 'Interstitial lung disease',
    option_d: 'Pulmonary embolism',
    option_e: 'Pneumonia',
    correct_answer: 'B',
    explanation: 'FEV1/FVC ratio <0.7 indicates obstructive lung disease. Given the smoking history and progressive dyspnoea, COPD is the most likely diagnosis.',
    category: 'Respiratory',
    difficulty: 'easy',
    tags: ['Respiratory', 'COPD', 'Spirometry', 'AMC'],
    citation: 'AMC Clinical Examination, 8th Edition, Chapter 8: Respiratory System',
    created_at: '2024-01-03T00:00:00Z',
    updated_at: '2024-01-03T00:00:00Z',
  },
];

/**
 * Sample MCQs for Psychiatry category
 */
export const PSYCHIATRY_MCQS: MCQFixture[] = [
  {
    id: 4,
    question: 'A 25-year-old woman reports hearing voices commenting on her actions. What is this symptom called?',
    option_a: 'First-rank symptom',
    option_b: 'Second-person auditory hallucination',
    option_c: 'Third-person auditory hallucination',
    option_d: 'Thought insertion',
    option_e: 'Running commentary',
    correct_answer: 'E',
    explanation: 'Running commentary (voices describing actions) is a first-rank symptom of schizophrenia. This is also considered a third-person auditory hallucination.',
    category: 'Psychiatry',
    difficulty: 'medium',
    tags: ['Psychiatry', 'Psychosis', 'Schizophrenia', 'AMC'],
    citation: 'AMC Clinical Examination, 8th Edition, Chapter 15: Psychiatric Assessment',
    created_at: '2024-01-04T00:00:00Z',
    updated_at: '2024-01-04T00:00:00Z',
  },
];

/**
 * All sample MCQs combined
 */
export const ALL_MCQS: MCQFixture[] = [
  ...CARDIOLOGY_MCQS,
  ...RESPIRATORY_MCQS,
  ...PSYCHIATRY_MCQS,
];

/**
 * MCQ with image (for testing image display)
 */
export const MCQ_WITH_IMAGE: MCQFixture = {
  id: 5,
  question: 'What ECG finding is shown in the image below?',
  option_a: 'Normal sinus rhythm',
  option_b: 'Atrial fibrillation',
  option_c: 'Atrial flutter',
  option_d: 'Ventricular tachycardia',
  option_e: 'Complete heart block',
  correct_answer: 'B',
  explanation: 'The ECG shows irregularly irregular rhythm with absent P waves, characteristic of atrial fibrillation.',
  category: 'Cardiology',
  difficulty: 'medium',
  tags: ['Cardiology', 'ECG', 'Arrhythmia', 'AMC'],
  image_url: 'https://example.com/ecg-af.png',
  citation: 'ECG Interpretation Guide, 5th Edition',
  created_at: '2024-01-05T00:00:00Z',
  updated_at: '2024-01-05T00:00:00Z',
};

/**
 * Generate paginated MCQ response
 */
export function generateMCQListResponse(
  skip: number = 0,
  limit: number = 20,
  category?: string,
  difficulty?: string
) {
  let filtered = [...ALL_MCQS];

  if (category) {
    filtered = filtered.filter((mcq) => mcq.category === category);
  }

  if (difficulty) {
    filtered = filtered.filter((mcq) => mcq.difficulty === difficulty);
  }

  const total = filtered.length;
  const items = filtered.slice(skip, skip + limit);

  return {
    items,
    total,
    skip,
    limit,
  };
}

/**
 * MCQ categories for dropdown testing
 */
export const MCQ_CATEGORIES = [
  'Cardiology',
  'Respiratory',
  'Psychiatry',
  'Surgery',
  'Medicine',
  'ObGyn',
  'Paediatrics',
];

/**
 * MCQ tags for filtering testing
 */
export const MCQ_TAGS = [
  'Acute',
  'Emergency',
  'Chronic',
  'AMC',
  'Diagnosis',
  'Management',
  'Investigation',
];
