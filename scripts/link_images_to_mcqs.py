#!/usr/bin/env python3
"""
Link Medical Images to MCQs
Matches images from unified catalog to MCQs based on specialty, topic, and keywords
Following IMAGE_LINKING_STRATEGY.md algorithm
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime
from collections import defaultdict


class ImageMatcher:
    """Match images to MCQs using clinical keyword and specialty matching"""

    def __init__(self, catalog_path: str, mcq_dir: str):
        self.catalog_path = Path(catalog_path)
        self.mcq_dir = Path(mcq_dir)
        self.catalog = None
        self.images_by_specialty = defaultdict(list)
        self.load_catalog()

    def load_catalog(self):
        """Load unified image catalog and index by specialty"""
        print(f"Loading image catalog from {self.catalog_path}...")

        with open(self.catalog_path, 'r') as f:
            self.catalog = json.load(f)

        print(f"Loaded {self.catalog['total_images']} images")

        # Index images by specialty for faster lookup
        for img in self.catalog['images']:
            specialty = img.get('specialty', '').lower()
            self.images_by_specialty[specialty].append(img)

        print(f"Indexed images across {len(self.images_by_specialty)} specialties")

    def extract_clinical_keywords(self, text: str) -> List[str]:
        """Extract clinical keywords from text using medical terminology patterns"""

        if not text:
            return []

        # Comprehensive medical keyword patterns
        patterns = [
            # Cardiac conditions
            r'\b(STEMI|NSTEMI|myocardial infarction|MI|angina|pericarditis|endocarditis)\b',
            r'\b(atrial fibrillation|AF|SVT|ventricular tachycardia|VT|bradycardia)\b',
            r'\b(heart failure|HF|cardiomyopathy|valve disease|stenosis|regurgitation)\b',
            r'\b(hypertension|HTN|aortic dissection|aneurysm)\b',

            # Respiratory conditions
            r'\b(pneumothorax|haemothorax|pneumonia|tuberculosis|TB|empyema)\b',
            r'\b(COPD|asthma|bronchiectasis|ILD|interstitial lung disease)\b',
            r'\b(PE|pulmonary embolism|DVT|thrombosis|pleural effusion)\b',
            r'\b(ARDS|respiratory failure|pneumonitis)\b',

            # Neurological conditions
            r'\b(stroke|CVA|haemorrhage|hemorrhage|infarction|ischaemia|ischemia)\b',
            r'\b(SAH|subarachnoid|subdural|extradural|epidural)\b',
            r'\b(meningitis|encephalitis|abscess|brain tumour|tumor)\b',
            r'\b(seizure|epilepsy|head injury|TBI|concussion)\b',

            # GI conditions
            r'\b(appendicitis|cholecystitis|pancreatitis|diverticulitis)\b',
            r'\b(bowel obstruction|perforation|peritonitis|ischaemic bowel)\b',
            r'\b(cirrhosis|hepatitis|liver failure|ascites)\b',
            r'\b(GI bleed|haematemesis|melaena|peptic ulcer)\b',

            # Endocrine conditions
            r'\b(diabetes|DKA|ketoacidosis|hypoglycaemia|hypoglycemia)\b',
            r'\b(thyroid|hyperthyroid|hypothyroid|thyrotoxicosis)\b',
            r'\b(Addison|Cushing|adrenal|pituitary|acromegaly)\b',

            # Emergency/Trauma
            r'\b(fracture|dislocation|trauma|injury|rupture)\b',
            r'\b(shock|sepsis|septic|anaphylaxis)\b',
            r'\b(burns|poisoning|overdose)\b',

            # Imaging modalities
            r'\b(CT|MRI|X-ray|ultrasound|USS|ECG|EKG|echocardiogram|echo)\b',
            r'\b(angiography|mammogram|PET|scan)\b',

            # Anatomical locations
            r'\b(brain|cerebral|intracranial|spinal|skull)\b',
            r'\b(chest|lung|pulmonary|cardiac|thoracic|mediastinal)\b',
            r'\b(abdomen|abdominal|liver|spleen|kidney|pancreas|gallbladder)\b',
            r'\b(pelvis|pelvic|uterus|ovary|bladder|prostate)\b',

            # Clinical findings
            r'\b(acute|chronic|severe|mild|moderate|bilateral|unilateral)\b',
            r'\b(ST elevation|ST segment elevation|ST depression|ST segment depression)\b',
            r'\b(T wave|T-wave|QRS|Q wave|Q-wave)\b',
            r'\b(consolidation|infiltrate|effusion|oedema|edema|mass|lesion)\b',
            r'\b(stenosis|occlusion|thrombus|haemorrhage|haematoma)\b',

            # Additional specific terms
            r'\b(infarction|ischemia|ischaemia|necrosis)\b',
            r'\b(elevation|depression)\b',  # Catch ST segment context

            # Psychiatric conditions and symptoms
            r'\b(depression|depressive|major depressive disorder|MDD)\b',
            r'\b(anxiety|GAD|panic|phobia|OCD)\b',
            r'\b(psychosis|psychotic|schizophrenia|delusions|hallucinations)\b',
            r'\b(bipolar|mania|manic|hypomania)\b',
            r'\b(suicide|suicidal|self-harm|deliberate self-harm)\b',
            r'\b(dementia|Alzheimer|Alzheimer\'s|cognitive decline|memory loss)\b',
            r'\b(delirium|confusion|altered mental state)\b',
            r'\b(PTSD|post-traumatic|trauma-related)\b',
            r'\b(anorexia|bulimia|eating disorder)\b',
            r'\b(ADHD|attention deficit|autism|ASD)\b',
            r'\b(personality disorder|borderline|antisocial)\b',
            r'\b(substance abuse|addiction|withdrawal|intoxication)\b',
            r'\b(antidepressant|SSRI|antipsychotic|lithium|mood stabilizer)\b',

            # Obstetrics & Gynaecology
            r'\b(ectopic pregnancy|ectopic|tubal pregnancy)\b',
            r'\b(miscarriage|spontaneous abortion|threatened abortion|incomplete abortion)\b',
            r'\b(molar pregnancy|hydatidiform mole|gestational trophoblastic)\b',
            r'\b(placenta previa|placental abruption|antepartum haemorrhage|antepartum hemorrhage|APH)\b',
            r'\b(pre-eclampsia|preeclampsia|eclampsia|HELLP|pregnancy induced hypertension)\b',
            r'\b(foetal|fetal|congenital anomaly|chromosomal abnormality|birth defect)\b',
            r'\b(nuchal translucency|Down syndrome|trisomy|Edwards syndrome|Patau)\b',
            r'\b(postpartum haemorrhage|postpartum hemorrhage|PPH|retained placenta)\b',
            r'\b(ovarian cyst|ovarian torsion|endometriosis|endometrioma)\b',
            r'\b(fibroids|uterine fibroid|leiomyoma|myoma)\b',
            r'\b(cervical cancer|cervical screening|HPV|cervical intraepithelial)\b',
            r'\b(pelvic inflammatory disease|PID|adnexal mass|tubo-ovarian)\b',
            r'\b(intrauterine growth restriction|IUGR|small for gestational age|SGA)\b',
            r'\b(gestational diabetes|GDM|pregnancy diabetes)\b',
            r'\b(hyperemesis gravidarum|severe morning sickness)\b',

            # Paediatrics
            r'\b(neonatal|newborn|neonate|birth asphyxia)\b',
            r'\b(prematurity|premature|preterm|RDS|respiratory distress syndrome)\b',
            r'\b(jaundice|hyperbilirubinaemia|hyperbilirubinemia|kernicterus)\b',
            r'\b(meconium|meconium aspiration|meconium ileus)\b',
            r'\b(congenital heart disease|VSD|ASD|PDA|tetralogy|coarctation)\b',
            r'\b(childhood|pediatric|paediatric|infant|toddler)\b',
            r'\b(developmental delay|developmental milestone|growth chart|failure to thrive)\b',
            r'\b(immunisation|immunization|vaccination|vaccine schedule)\b',
            r'\b(febrile seizure|febrile convulsion|infantile spasm)\b',
            r'\b(bronchiolitis|croup|whooping cough|pertussis|RSV)\b',
            r'\b(rickets|vitamin D deficiency|bowed legs|rachitic)\b',
            r'\b(kawasaki|intussusception|pyloric stenosis|hirschsprung)\b',
            r'\b(necrotizing enterocolitis|NEC|neonatal sepsis)\b',
            r'\b(cerebral palsy|developmental dysplasia|hip dysplasia|DDH)\b',

            # Dermatology (clinical terms)
            r'\b(rash|eruption|exanthem|skin lesion)\b',
            r'\b(erythema|erythematous|red patch|redness)\b',
            r'\b(vesicle|bullae|blistering|blister|pustule)\b',
            r'\b(macule|papule|nodule|plaque|wheal)\b',
            r'\b(pigmentation|hyperpigmentation|hypopigmentation|depigmentation)\b',
            r'\b(pruritus|itching|itch|pruritic)\b',
            r'\b(eczema|atopic dermatitis|psoriasis|dermatitis)\b',
            r'\b(melanoma|basal cell carcinoma|squamous cell carcinoma|skin cancer)\b',
            r'\b(cellulitis|abscess|skin infection|impetigo)\b',
            r'\b(urticaria|hives|angioedema)\b',
            r'\b(acne|acne vulgaris|comedone)\b',
            r'\b(vitiligo|alopecia|hair loss)\b',

            # Neurology
            r'\b(stroke|CVA|cerebrovascular accident|ischaemic stroke|ischemic stroke|hemorrhagic stroke)\b',
            r'\b(TIA|transient ischaemic attack|transient ischemic attack|mini stroke)\b',
            r'\b(seizure|epilepsy|status epilepticus|convulsion|fits)\b',
            r'\b(headache|migraine|cluster headache|tension headache|cephalalgia)\b',
            r'\b(brain hemorrhage|brain haemorrhage|ICH|SAH|subdural|epidural|intracranial hemorrhage)\b',
            r'\b(meningitis|encephalitis|brain abscess|CNS infection)\b',
            r'\b(neuropathy|peripheral neuropathy|diabetic neuropathy|polyneuropathy)\b',
            r'\b(multiple sclerosis|MS|demyelinating|demyelination)\b',
            r'\b(parkinson|parkinsonism|tremor|bradykinesia|rigidity)\b',
            r'\b(brain tumour|brain tumor|intracranial mass|glioma|meningioma)\b',
            r'\b(guillain-barre|GBS|ascending paralysis)\b',
            r'\b(myasthenia gravis|MG|neuromuscular junction)\b',
            r'\b(motor neurone disease|MND|ALS|amyotrophic lateral sclerosis)\b',
            r'\b(vertigo|dizziness|BPPV|vestibular)\b',
            r'\b(bell palsy|facial nerve palsy|facial weakness)\b',

            # Gastroenterology
            r'\b(peptic ulcer|gastric ulcer|duodenal ulcer|H pylori|helicobacter)\b',
            r'\b(GORD|GERD|reflux|heartburn|gastro-oesophageal reflux|gastroesophageal reflux)\b',
            r'\b(IBD|inflammatory bowel disease|Crohn|ulcerative colitis|UC)\b',
            r'\b(cirrhosis|liver failure|hepatic encephalopathy|portal hypertension)\b',
            r'\b(hepatitis|viral hepatitis|liver inflammation|hepatocellular)\b',
            r'\b(pancreatitis|pancreatic|acute pancreatitis|chronic pancreatitis)\b',
            r'\b(cholecystitis|gallstones|biliary colic|cholelithiasis|cholangitis)\b',
            r'\b(bowel obstruction|ileus|volvulus|intestinal obstruction)\b',
            r'\b(diverticulitis|diverticular disease|diverticulosis)\b',
            r'\b(coeliac disease|celiac disease|gluten|malabsorption)\b',
            r'\b(appendicitis|appendix|right iliac fossa|RIF pain)\b',
            r'\b(colorectal cancer|colon cancer|bowel cancer|colonoscopy)\b',
            r'\b(liver cancer|hepatocellular carcinoma|HCC)\b',
            r'\b(ascites|peritonitis|abdominal fluid)\b',
            r'\b(oesophageal|esophageal|varices|dysphagia)\b',
            r'\b(gastritis|gastroenteritis|diarrhoea|diarrhea)\b',

            # Endocrinology
            r'\b(diabetes|diabetic|hyperglycemia|hyperglycaemia|hypoglycemia|hypoglycaemia|DKA|diabetic ketoacidosis)\b',
            r'\b(type 1 diabetes|type 2 diabetes|T1DM|T2DM|insulin)\b',
            r'\b(thyroid|hyperthyroid|hypothyroid|thyrotoxicosis|Graves|Hashimoto)\b',
            r'\b(thyroid storm|myxoedema|myxedema|goitre|goiter)\b',
            r'\b(Cushing|hypercortisolism|adrenal insufficiency|Addison)\b',
            r'\b(pheochromocytoma|phaeochromocytoma|adrenal tumor|adrenal tumour)\b',
            r'\b(acromegaly|growth hormone|gigantism|pituitary)\b',
            r'\b(hypercalcemia|hypercalcaemia|hypocalcemia|hypocalcaemia|hyperparathyroid|hypoparathyroid)\b',
            r'\b(osteoporosis|osteopenia|bone density|fracture risk)\b',
            r'\b(metabolic syndrome|obesity|BMI|weight management)\b',
            r'\b(hyperlipidemia|hyperlipidaemia|cholesterol|statin|lipid)\b',
            r'\b(polycystic ovary|PCOS|ovarian cyst)\b',
            r'\b(prolactinoma|hyperprolactinaemia|hyperprolactinemia)\b',
        ]

        keywords = set()
        text_lower = text.lower()

        for pattern in patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            keywords.update([m.lower() for m in matches])

        return list(keywords)

    def normalize_specialty(self, specialty: str) -> str:
        """Normalize specialty names to match catalog format"""

        specialty_map = {
            'cardiology': 'cardiology',
            'respiratory': 'respiratory',
            'neurology': 'neurology',
            'gastroenterology': 'gastroenterology',
            'gastrointestinal': 'gastroenterology',
            'endocrinology': 'endocrinology',
            'emergency medicine': 'emergency_medicine',
            'emergency_medicine': 'emergency_medicine',
            'dermatology': 'dermatology',
            'hematology': 'hematology',
            'haematology': 'hematology',
            'psychiatry': 'psychiatry',
            'obstetrics': 'obstetrics',
            'gynaecology': 'gynaecology',
            'gynecology': 'gynaecology',
            'paediatrics': 'paediatrics',
            'pediatrics': 'paediatrics',
        }

        spec_lower = specialty.lower().strip()
        return specialty_map.get(spec_lower, spec_lower)

    def extract_mcq_keywords(self, mcq: Dict) -> Tuple[List[str], str]:
        """Extract keywords and specialty from MCQ"""

        # Get and normalize specialty
        specialty = self.normalize_specialty(mcq.get('specialty', ''))

        # Extract text from all MCQ components
        text_parts = []

        # Question structure can be dict or string
        question = mcq.get('question', {})
        if isinstance(question, dict):
            text_parts.append(question.get('scenario', ''))
            text_parts.append(question.get('stem', ''))

            # Extract options
            options = question.get('options', {})
            if isinstance(options, dict):
                text_parts.extend(options.values())
        else:
            text_parts.append(str(question))

        # Also include topic and subtopic
        text_parts.append(mcq.get('topic', ''))
        text_parts.append(mcq.get('subtopic', ''))
        text_parts.append(mcq.get('explanation', ''))

        # Combine all text
        combined_text = ' '.join(str(part) for part in text_parts if part)

        # Extract keywords
        keywords = self.extract_clinical_keywords(combined_text)

        return keywords, specialty

    def calculate_match_score(self, img: Dict, mcq_specialty: str, mcq_keywords: List[str],
                             mcq_topic: str = '') -> Tuple[int, str]:
        """
        Calculate match score between image and MCQ

        Returns: (score, reason)

        Scoring:
        - Exact specialty + topic match: 100
        - Specialty match + keyword overlap ≥2: 50 + 10 × overlap count
        - Keyword overlap ≥3: 30 + 5 × overlap count
        """

        img_specialty = img.get('specialty', '').lower()
        img_topic = img.get('topic', '').lower().replace('_', ' ')

        # Get image keywords - if None, extract from title and topic
        img_keywords = img.get('keywords', [])
        if not img_keywords or img_keywords is None:
            # Extract keywords from image title and topic
            img_text = f"{img.get('title', '')} {img.get('topic', '')}"
            img_keywords = self.extract_clinical_keywords(img_text)

        img_keywords = set(img_keywords if img_keywords else [])

        mcq_specialty_norm = mcq_specialty.lower()
        mcq_topic_norm = mcq_topic.lower()
        mcq_keywords_set = set(mcq_keywords)

        # Calculate keyword overlap
        keyword_overlap = img_keywords & mcq_keywords_set
        overlap_count = len(keyword_overlap)

        # Match 1: Exact specialty + topic match (score: 100)
        if img_specialty == mcq_specialty_norm and mcq_topic_norm and img_topic in mcq_topic_norm:
            return 100, f"exact_topic: {img_specialty}/{img_topic}"

        # Match 2: Specialty match + keyword overlap ≥2 (score: 50 + 10 × overlap)
        if img_specialty == mcq_specialty_norm and overlap_count >= 2:
            score = 50 + (overlap_count * 10)
            keywords_matched = ', '.join(list(keyword_overlap)[:3])
            return score, f"specialty_keywords: {overlap_count} matches ({keywords_matched})"

        # Match 3: Keyword overlap ≥2 (score: 30 + 5 × overlap) - LOWERED from ≥3 to ≥2
        if overlap_count >= 2:
            score = 30 + (overlap_count * 5)
            keywords_matched = ', '.join(list(keyword_overlap)[:3])
            return score, f"keyword_overlap: {overlap_count} matches ({keywords_matched})"

        return 0, "no_match"

    def find_matching_images(self, mcq: Dict, top_n: int = 3) -> List[Dict]:
        """Find top N matching images for an MCQ"""

        # Extract MCQ metadata
        mcq_keywords, mcq_specialty = self.extract_mcq_keywords(mcq)
        mcq_topic = mcq.get('topic', '')

        # Get candidate images from same specialty
        specialty_images = self.images_by_specialty.get(mcq_specialty.lower(), [])

        # If no specialty match, try all images (for keyword-only matches)
        if not specialty_images:
            specialty_images = self.catalog['images']

        # Calculate match scores
        matches = []
        for img in specialty_images:
            score, reason = self.calculate_match_score(
                img, mcq_specialty, mcq_keywords, mcq_topic
            )

            if score > 0:
                # Get path - HEAL images use 'filename', OpenI use 'path'
                image_path = img.get('path') or img.get('filename', '')

                matches.append({
                    'image_id': img['id'],
                    'path': image_path,
                    'match_score': score,
                    'match_reason': reason,
                    'image_title': img.get('title', ''),
                    'image_topic': img.get('topic', ''),
                    'source': img.get('source', '')
                })

        # Sort by score (descending) and return top N
        matches.sort(key=lambda x: x['match_score'], reverse=True)
        return matches[:top_n]

    def process_mcq_file(self, mcq_file: Path) -> Tuple[List[Dict], Dict]:
        """Process a single MCQ file and return matches"""

        print(f"\nProcessing {mcq_file.name}...")

        with open(mcq_file, 'r') as f:
            data = json.load(f)

        # Handle different MCQ file structures
        mcqs = data.get('mcqs', [])
        if not mcqs and isinstance(data, list):
            mcqs = data

        print(f"Found {len(mcqs)} MCQs")

        matches = {}
        stats = {
            'file_name': mcq_file.name,
            'total_mcqs': len(mcqs),
            'matched_mcqs': 0,
            'match_distribution': defaultdict(int),
            'specialty_breakdown': defaultdict(lambda: {'total': 0, 'matched': 0})
        }

        for i, mcq in enumerate(mcqs, 1):
            if i % 50 == 0:
                print(f"  Processed {i}/{len(mcqs)} MCQs...")

            mcq_id = mcq.get('id', f'MCQ_{i}')
            # Use normalized specialty for stats consistency
            specialty = self.normalize_specialty(mcq.get('specialty', 'unknown'))

            # Find matching images
            matched_images = self.find_matching_images(mcq, top_n=3)

            if matched_images:
                matches[mcq_id] = matched_images
                stats['matched_mcqs'] += 1
                stats['specialty_breakdown'][specialty]['matched'] += 1

                # Track match score distribution
                top_score = matched_images[0]['match_score']
                if top_score >= 80:
                    stats['match_distribution']['excellent (≥80)'] += 1
                elif top_score >= 60:
                    stats['match_distribution']['good (60-79)'] += 1
                elif top_score >= 40:
                    stats['match_distribution']['fair (40-59)'] += 1
                else:
                    stats['match_distribution']['weak (<40)'] += 1

            stats['specialty_breakdown'][specialty]['total'] += 1

        if len(mcqs) > 0:
            print(f"  Matched {stats['matched_mcqs']}/{len(mcqs)} MCQs ({stats['matched_mcqs']/len(mcqs)*100:.1f}%)")
        else:
            print(f"  Skipping empty file")

        return matches, stats

    def process_all_mcqs(self) -> Dict:
        """Process all MCQ files in the directory"""

        print(f"\nSearching for MCQ files in {self.mcq_dir}...")

        # Find all JSON files in MCQ directory
        mcq_files = list(self.mcq_dir.glob('*.json'))
        mcq_files = [f for f in mcq_files if 'image_matches' not in f.name]  # Exclude output files

        print(f"Found {len(mcq_files)} MCQ files")

        all_matches = {}
        all_stats = []

        for mcq_file in sorted(mcq_files):
            matches, stats = self.process_mcq_file(mcq_file)
            all_matches.update(matches)
            all_stats.append(stats)

        # Aggregate statistics
        total_stats = self._aggregate_statistics(all_stats)

        return {
            'generated_at': datetime.now().isoformat(),
            'catalog_path': str(self.catalog_path),
            'total_images_available': self.catalog['total_images'],
            'total_mcqs_processed': total_stats['total_mcqs'],
            'total_mcqs_matched': total_stats['matched_mcqs'],
            'match_rate': f"{total_stats['matched_mcqs']/total_stats['total_mcqs']*100:.1f}%" if total_stats['total_mcqs'] > 0 else "0%",
            'matches': all_matches,
            'statistics': total_stats,
            'file_breakdown': all_stats
        }

    def _aggregate_statistics(self, all_stats: List[Dict]) -> Dict:
        """Aggregate statistics from all files"""

        total = {
            'total_mcqs': 0,
            'matched_mcqs': 0,
            'match_distribution': defaultdict(int),
            'specialty_breakdown': defaultdict(lambda: {'total': 0, 'matched': 0})
        }

        for stats in all_stats:
            total['total_mcqs'] += stats['total_mcqs']
            total['matched_mcqs'] += stats['matched_mcqs']

            for category, count in stats['match_distribution'].items():
                total['match_distribution'][category] += count

            for specialty, counts in stats['specialty_breakdown'].items():
                total['specialty_breakdown'][specialty]['total'] += counts['total']
                total['specialty_breakdown'][specialty]['matched'] += counts['matched']

        # Convert defaultdicts to regular dicts for JSON serialization
        total['match_distribution'] = dict(total['match_distribution'])
        total['specialty_breakdown'] = dict(total['specialty_breakdown'])

        return total

    def save_results(self, results: Dict, output_path: Path):
        """Save matching results to JSON file"""

        print(f"\nSaving results to {output_path}...")

        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"Results saved successfully")

    def print_summary(self, results: Dict):
        """Print summary statistics"""

        stats = results['statistics']

        print("\n" + "="*70)
        print("IMAGE MATCHING SUMMARY")
        print("="*70)
        print(f"\nTotal MCQs processed: {stats['total_mcqs']}")
        print(f"MCQs with matched images: {stats['matched_mcqs']}")
        print(f"Match rate: {results['match_rate']}")

        print(f"\nMatch Quality Distribution:")
        for category, count in sorted(stats['match_distribution'].items()):
            pct = count / stats['matched_mcqs'] * 100 if stats['matched_mcqs'] > 0 else 0
            print(f"  {category}: {count} ({pct:.1f}%)")

        print(f"\nSpecialty Breakdown:")
        for specialty, counts in sorted(stats['specialty_breakdown'].items()):
            pct = counts['matched'] / counts['total'] * 100 if counts['total'] > 0 else 0
            print(f"  {specialty}: {counts['matched']}/{counts['total']} ({pct:.1f}%)")

        print("\n" + "="*70)


def main():
    """Main execution"""

    # Configuration
    catalog_path = "data/medical_images/unified_image_catalog.json"
    mcq_dir = "data/mcqs"
    output_path = "data/mcqs/mcq_image_matches.json"

    print("="*70)
    print("MCQ IMAGE MATCHING SYSTEM")
    print("="*70)
    print(f"\nCatalog: {catalog_path}")
    print(f"MCQ directory: {mcq_dir}")
    print(f"Output: {output_path}")

    # Initialize matcher
    matcher = ImageMatcher(catalog_path, mcq_dir)

    # Process all MCQs
    results = matcher.process_all_mcqs()

    # Save results
    matcher.save_results(results, Path(output_path))

    # Print summary
    matcher.print_summary(results)

    print(f"\n✓ Image matching complete!")
    print(f"✓ Results saved to: {output_path}")


if __name__ == '__main__':
    main()
