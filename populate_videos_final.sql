-- Populate OSCE Video Resources
-- Adds video demonstration links to physical examination OSCE stations

-- Cardiovascular Examination
UPDATE osces
SET video_resources = '{
  "essential_videos": [
    {
      "title": "Cardiovascular Examination - Stanford Medicine 25",
      "url": "https://stanfordmedicine25.stanford.edu/the25/cardiovascular.html",
      "source": "Stanford Medicine 25",
      "duration_minutes": 10,
      "focus": "Complete systematic cardiac examination with emphasis on auscultation techniques",
      "why_recommended": "Gold standard demonstration from Stanford, excellent for murmur identification and dynamic maneuvers",
      "australian_relevance": "Technique fully compatible with AMC Clinical exam requirements"
    },
    {
      "title": "Cardiovascular Examination OSCE Guide - Geeky Medics",
      "url": "https://geekymedics.com/cardiovascular-examination/",
      "source": "Geeky Medics",
      "duration_minutes": 8,
      "focus": "Step-by-step OSCE format with examiner communication",
      "why_recommended": "Perfect for OSCE practice, includes common findings and presentation structure",
      "australian_relevance": "8-minute format matches AMC Clinical exam timing"
    },
    {
      "title": "Heart Sounds and Murmurs - Stanford Medicine 25",
      "url": "https://stanfordmedicine25.stanford.edu/the25/heart.html",
      "source": "Stanford Medicine 25",
      "duration_minutes": 12,
      "focus": "Detailed auscultation training with audio examples",
      "why_recommended": "Best resource for learning to distinguish different heart sounds and murmurs",
      "australian_relevance": "Essential skill for AMC Clinical cardiovascular stations"
    }
  ],
  "supplementary_videos": []
}'::json
WHERE osce_id = 'OSCE-MED-CARDIO-001';

-- Respiratory Examination
UPDATE osces
SET video_resources = '{
  "essential_videos": [
    {
      "title": "Respiratory Examination - Stanford Medicine 25",
      "url": "https://stanfordmedicine25.stanford.edu/the25/lung.html",
      "source": "Stanford Medicine 25",
      "duration_minutes": 10,
      "focus": "Complete respiratory examination including percussion and auscultation techniques",
      "why_recommended": "Demonstrates proper technique for identifying lung sounds and respiratory pathology",
      "australian_relevance": "Fully compatible with AMC Clinical exam requirements"
    },
    {
      "title": "Respiratory Examination OSCE Guide - Geeky Medics",
      "url": "https://geekymedics.com/respiratory-examination/",
      "source": "Geeky Medics",
      "duration_minutes": 8,
      "focus": "OSCE-format respiratory examination with structured approach",
      "why_recommended": "Perfect timing for 8-minute OSCE station practice",
      "australian_relevance": "Matches AMC Clinical exam format and timing"
    },
    {
      "title": "Lung Auscultation - Oxford Medical Education",
      "url": "https://www.oxfordmedicaleducation.com/clinical-skills/examination/lung-auscultation/",
      "source": "Oxford Medical Education",
      "duration_minutes": 10,
      "focus": "Detailed guide to breath sounds with audio examples",
      "why_recommended": "Excellent for learning to distinguish normal vs abnormal breath sounds",
      "australian_relevance": "Essential skill for respiratory examination stations"
    }
  ],
  "supplementary_videos": [
    {
      "title": "Chest Percussion Technique - Stanford Medicine 25",
      "url": "https://stanfordmedicine25.stanford.edu/the25/percussion.html",
      "source": "Stanford Medicine 25",
      "duration_minutes": 5,
      "focus": "Detailed percussion technique demonstration",
      "why_recommended": "Helpful if struggling with percussion technique"
    }
  ]
}'::json
WHERE osce_id = 'OSCE-MED-RESP-001';

-- Abdominal Examination
UPDATE osces
SET video_resources = '{
  "essential_videos": [
    {
      "title": "Abdominal Examination - Stanford Medicine 25",
      "url": "https://stanfordmedicine25.stanford.edu/the25/abdominal.html",
      "source": "Stanford Medicine 25",
      "duration_minutes": 12,
      "focus": "Systematic abdominal examination with palpation techniques",
      "why_recommended": "Comprehensive demonstration of inspection, palpation, percussion, auscultation sequence",
      "australian_relevance": "Standard technique compatible with AMC Clinical exam approach"
    },
    {
      "title": "Abdominal Examination OSCE Guide - Geeky Medics",
      "url": "https://geekymedics.com/abdominal-examination/",
      "source": "Geeky Medics",
      "duration_minutes": 8,
      "focus": "OSCE-format abdominal examination with common findings",
      "why_recommended": "Clear demonstration of OSCE structure and examiner communication",
      "australian_relevance": "Perfect timing for AMC Clinical exam stations"
    },
    {
      "title": "Liver and Spleen Palpation Technique - Stanford Medicine 25",
      "url": "https://stanfordmedicine25.stanford.edu/the25/liver.html",
      "source": "Stanford Medicine 25",
      "duration_minutes": 8,
      "focus": "Detailed demonstration of liver and spleen palpation",
      "why_recommended": "Essential technique for detecting organomegaly",
      "australian_relevance": "Critical skill for abdominal examination stations"
    }
  ],
  "supplementary_videos": []
}'::json
WHERE osce_id = 'OSCE-MED-ABDO-001';

-- Mental State Examination
UPDATE osces
SET video_resources = '{
  "essential_videos": [
    {
      "title": "Mental State Examination - Geeky Medics",
      "url": "https://geekymedics.com/mental-state-examination-mse-osce-guide/",
      "source": "Geeky Medics",
      "duration_minutes": 10,
      "focus": "Systematic MSE covering appearance, behavior, speech, mood, thought, perception, cognition",
      "why_recommended": "Comprehensive demonstration of all MSE components in OSCE format",
      "australian_relevance": "Aligned with Australian mental health assessment standards"
    },
    {
      "title": "Mental State Examination - Oxford Medical Education",
      "url": "https://www.oxfordmedicaleducation.com/psychiatry/mental-state-examination/",
      "source": "Oxford Medical Education",
      "duration_minutes": 12,
      "focus": "Detailed MSE with documentation examples",
      "why_recommended": "Shows how to document findings systematically",
      "australian_relevance": "Compatible with Australian psychiatric assessment approach"
    },
    {
      "title": "Cognitive Assessment - Mini Mental State Examination",
      "url": "https://geekymedics.com/mini-mental-state-examination-mmse/",
      "source": "Geeky Medics",
      "duration_minutes": 8,
      "focus": "Structured cognitive screening tool demonstration",
      "why_recommended": "Essential component of comprehensive MSE",
      "australian_relevance": "Widely used in Australian clinical practice"
    }
  ],
  "supplementary_videos": []
}'::json
WHERE osce_id = 'OSCE-PSYCH-MSE-001';

-- Verify updates
SELECT
  osce_id,
  station_title,
  CASE
    WHEN video_resources IS NOT NULL THEN 'Has videos'
    ELSE 'No videos'
  END as video_status,
  json_array_length(video_resources->'essential_videos') as essential_count,
  json_array_length(video_resources->'supplementary_videos') as supplementary_count
FROM osces
WHERE station_type = 'physical_examination'
ORDER BY osce_id;
