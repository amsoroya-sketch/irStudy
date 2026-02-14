-- Populate OSCE Video Resources
-- This SQL script adds video demonstration links to physical examination OSCE stations

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
      "why_recommended": "Perfect for OSCE practice, includes common findings and presentation structure"
    }
  ],
  "supplementary_videos": []
}'::jsonb
WHERE station_title ILIKE '%cardiovascular%'
  AND station_type = 'physical_examination';

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
      "why_recommended": "Clear demonstration of OSCE structure and examiner communication"
    }
  ],
  "supplementary_videos": []
}'::jsonb
WHERE station_title ILIKE '%abdominal%'
  AND station_type = 'physical_examination';

-- Respiratory Examination
UPDATE osces
SET video_resources = '{
  "essential_videos": [
    {
      "title": "Respiratory Examination - Stanford Medicine 25",
      "url": "https://stanfordmedicine25.stanford.edu/the25/respiratory.html",
      "source": "Stanford Medicine 25",
      "duration_minutes": 10,
      "focus": "Complete respiratory examination including percussion and auscultation",
      "why_recommended": "Demonstrates proper technique for identifying lung sounds and respiratory pathology",
      "australian_relevance": "Fully compatible with AMC Clinical exam requirements"
    },
    {
      "title": "Respiratory Examination OSCE Guide - Geeky Medics",
      "url": "https://geekymedics.com/respiratory-examination/",
      "source": "Geeky Medics",
      "duration_minutes": 8,
      "focus": "OSCE-format respiratory examination with structured approach",
      "why_recommended": "Perfect timing for 8-minute OSCE station practice"
    }
  ],
  "supplementary_videos": []
}'::jsonb
WHERE station_title ILIKE '%respiratory%'
  AND station_type = 'physical_examination';

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
      "why_recommended": "Shows how to document findings systematically"
    }
  ],
  "supplementary_videos": []
}'::jsonb
WHERE station_title ILIKE '%mental state%'
  AND station_type = 'physical_examination';

-- Verify updates
SELECT
  id,
  station_title,
  CASE
    WHEN video_resources IS NOT NULL THEN 'Has videos'
    ELSE 'No videos'
  END as video_status,
  jsonb_array_length(video_resources->'essential_videos') as video_count
FROM osces
WHERE station_type = 'physical_examination'
ORDER BY id;
