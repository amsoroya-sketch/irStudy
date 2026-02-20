/**
 * OSCE Test Data Fixtures
 * Includes OSCEs with and without video resources for comprehensive testing
 */

export interface VideoResource {
  title: string;
  url: string;
  source: string;
  duration_minutes?: number;
  focus: string;
  why_recommended: string;
  australian_relevance?: string;
}

export interface OSCETestData {
  osce_id: string;
  station_title: string;
  station_type: 'history_taking' | 'physical_examination' | 'counselling' | 'procedure' | 'communication' | 'emergency_scenario';
  specialty: string;
  difficulty: 'easy' | 'medium' | 'hard';
  time_limit_minutes: number;
  patient_instructions: string;
  candidate_instructions: string;
  examiner_instructions: string;
  rubric: any;
  learning_objectives: string[];
  key_points: string[];
  video_resources?: {
    essential_videos: VideoResource[];
    supplementary_videos: VideoResource[];
  };
  is_published: boolean;
}

/**
 * OSCE with full video resources (essential + supplementary)
 */
export const OSCE_WITH_FULL_VIDEOS: OSCETestData = {
  osce_id: 'TEST-CARDIO-VIDEO-001',
  station_title: 'Cardiovascular Physical Examination with Video Demonstrations',
  station_type: 'physical_examination',
  specialty: 'cardiology',
  difficulty: 'medium',
  time_limit_minutes: 8,
  patient_instructions: 'You are a patient attending cardiology clinic for examination. Remain relaxed and follow the doctor\'s instructions.',
  candidate_instructions: 'Perform a systematic cardiovascular examination. You have 8 minutes.',
  examiner_instructions: 'Observe the candidate\'s technique and mark using the rubric.',
  rubric: {
    criteria: [
      { item: 'Introduction and consent', points: 10 },
      { item: 'Systematic examination approach', points: 40 },
      { item: 'Correct technique', points: 30 },
      { item: 'Professionalism', points: 20 },
    ],
    total_points: 100,
    pass_mark: 60,
  },
  learning_objectives: [
    'Perform systematic cardiovascular examination',
    'Identify normal and abnormal cardiovascular signs',
    'Demonstrate appropriate auscultation technique',
  ],
  key_points: [
    'Always position patient at 45 degrees for JVP assessment',
    'Auscultate at 4 key areas: Aortic, Pulmonary, Tricuspid, Mitral (APTM)',
    'Check for peripheral signs (clubbing, cyanosis, edema)',
  ],
  video_resources: {
    essential_videos: [
      {
        title: 'Cardiovascular Examination - Stanford Medicine 25',
        url: 'https://stanfordmedicine25.stanford.edu/the25/cardiovascular.html',
        source: 'Stanford Medicine 25',
        duration_minutes: 10,
        focus: 'Complete systematic cardiac examination with emphasis on auscultation techniques',
        why_recommended: 'Gold standard demonstration from Stanford, excellent for murmur identification and dynamic maneuvers',
        australian_relevance: 'Technique fully compatible with AMC Clinical exam requirements',
      },
      {
        title: 'Heart Examination - Geeky Medics',
        url: 'https://geekymedics.com/cardiovascular-examination/',
        source: 'Geeky Medics',
        duration_minutes: 8,
        focus: 'Step-by-step cardiovascular examination',
        why_recommended: 'Clear, concise demonstration with OSCE-specific tips',
        australian_relevance: 'Widely used in Australian medical schools',
      },
    ],
    supplementary_videos: [
      {
        title: 'Advanced Auscultation Techniques - Oxford Medical Education',
        url: 'https://www.oxfordmedicaleducation.com/clinical-examination/cardiovascular-examination/',
        source: 'Oxford Medical Education',
        duration_minutes: 12,
        focus: 'Advanced heart sound identification',
        why_recommended: 'Detailed coverage of complex murmurs',
      },
    ],
  },
  is_published: true,
};

/**
 * OSCE with only essential videos (no supplementary)
 */
export const OSCE_WITH_ESSENTIAL_ONLY: OSCETestData = {
  osce_id: 'TEST-RESP-VIDEO-001',
  station_title: 'Respiratory Physical Examination',
  station_type: 'physical_examination',
  specialty: 'respiratory',
  difficulty: 'medium',
  time_limit_minutes: 8,
  patient_instructions: 'You are a patient with a respiratory complaint.',
  candidate_instructions: 'Perform a respiratory examination.',
  examiner_instructions: 'Mark systematic approach and technique.',
  rubric: {
    criteria: [{ item: 'Examination technique', points: 100 }],
    total_points: 100,
    pass_mark: 60,
  },
  learning_objectives: ['Perform respiratory examination'],
  key_points: ['Inspect, palpate, percuss, auscultate'],
  video_resources: {
    essential_videos: [
      {
        title: 'Respiratory Examination - Geeky Medics',
        url: 'https://geekymedics.com/respiratory-examination/',
        source: 'Geeky Medics',
        duration_minutes: 9,
        focus: 'Complete respiratory examination technique',
        why_recommended: 'Clear demonstration suitable for AMC Clinical exam',
      },
    ],
    supplementary_videos: [],
  },
  is_published: true,
};

/**
 * OSCE with NO videos
 */
export const OSCE_WITHOUT_VIDEOS: OSCETestData = {
  osce_id: 'TEST-NEURO-HISTORY-001',
  station_title: 'Neurological History Taking',
  station_type: 'history_taking',
  specialty: 'neurology',
  difficulty: 'medium',
  time_limit_minutes: 8,
  patient_instructions: 'You are presenting with headaches.',
  candidate_instructions: 'Take a focused neurological history.',
  examiner_instructions: 'Assess systematic history-taking.',
  rubric: {
    criteria: [{ item: 'History taking', points: 100 }],
    total_points: 100,
    pass_mark: 60,
  },
  learning_objectives: ['Take systematic neurological history'],
  key_points: ['Use SOCRATES framework for pain history'],
  // NO video_resources field
  is_published: true,
};

/**
 * OSCE with maximum videos (4 essential + 3 supplementary)
 */
export const OSCE_WITH_MAX_VIDEOS: OSCETestData = {
  osce_id: 'TEST-ABDO-VIDEO-001',
  station_title: 'Abdominal Examination - Comprehensive',
  station_type: 'physical_examination',
  specialty: 'gastroenterology',
  difficulty: 'hard',
  time_limit_minutes: 8,
  patient_instructions: 'You have abdominal discomfort.',
  candidate_instructions: 'Perform complete abdominal examination.',
  examiner_instructions: 'Assess systematic approach and technique.',
  rubric: {
    criteria: [{ item: 'Examination', points: 100 }],
    total_points: 100,
    pass_mark: 60,
  },
  learning_objectives: ['Complete abdominal examination'],
  key_points: ['Inspection, auscultation, percussion, palpation (correct order)'],
  video_resources: {
    essential_videos: [
      {
        title: 'Abdominal Examination Part 1 - Stanford',
        url: 'https://stanfordmedicine25.stanford.edu/the25/abdominal.html',
        source: 'Stanford Medicine 25',
        duration_minutes: 8,
        focus: 'Inspection and auscultation',
        why_recommended: 'Gold standard technique demonstration',
      },
      {
        title: 'Abdominal Examination Part 2 - Geeky Medics',
        url: 'https://geekymedics.com/abdominal-examination/',
        source: 'Geeky Medics',
        duration_minutes: 10,
        focus: 'Palpation and percussion techniques',
        why_recommended: 'OSCE-focused demonstration',
      },
      {
        title: 'Acute Abdomen Assessment - Oxford',
        url: 'https://www.oxfordmedicaleducation.com/clinical-examination/abdominal-examination/',
        source: 'Oxford Medical Education',
        duration_minutes: 7,
        focus: 'Identifying acute surgical abdomen',
        why_recommended: 'Emergency presentations focus',
      },
      {
        title: 'Liver Palpation Technique',
        url: 'https://geekymedics.com/liver-palpation/',
        source: 'Geeky Medics',
        duration_minutes: 5,
        focus: 'Specific liver examination technique',
        why_recommended: 'Detailed hepatomegaly assessment',
      },
    ],
    supplementary_videos: [
      {
        title: 'Abdominal Auscultation',
        url: 'https://geekymedics.com/bowel-sounds/',
        source: 'Geeky Medics',
        duration_minutes: 4,
        focus: 'Interpreting bowel sounds',
        why_recommended: 'Helps differentiate normal vs abnormal sounds',
      },
      {
        title: 'Ascites Assessment',
        url: 'https://stanfordmedicine25.stanford.edu/the25/ascites.html',
        source: 'Stanford Medicine 25',
        duration_minutes: 6,
        focus: 'Detecting and quantifying ascites',
        why_recommended: 'Shifting dullness and fluid thrill techniques',
      },
      {
        title: 'Hernias and Masses',
        url: 'https://geekymedics.com/hernia-examination/',
        source: 'Geeky Medics',
        duration_minutes: 8,
        focus: 'Identifying abdominal hernias',
        why_recommended: 'Common OSCE scenario',
      },
    ],
  },
  is_published: true,
};

/**
 * All test OSCEs for seeding
 */
export const TEST_OSCES: OSCETestData[] = [
  OSCE_WITH_FULL_VIDEOS,
  OSCE_WITH_ESSENTIAL_ONLY,
  OSCE_WITHOUT_VIDEOS,
  OSCE_WITH_MAX_VIDEOS,
];

/**
 * Helper to get OSCE by ID
 */
export function getOSCEById(id: string): OSCETestData | undefined {
  return TEST_OSCES.find(osce => osce.osce_id === id);
}

/**
 * Helper to get OSCEs with videos
 */
export function getOSCEsWithVideos(): OSCETestData[] {
  return TEST_OSCES.filter(osce => osce.video_resources &&
    (osce.video_resources.essential_videos.length > 0 ||
     osce.video_resources.supplementary_videos.length > 0));
}

/**
 * Helper to get OSCEs without videos
 */
export function getOSCEsWithoutVideos(): OSCETestData[] {
  return TEST_OSCES.filter(osce => !osce.video_resources);
}
