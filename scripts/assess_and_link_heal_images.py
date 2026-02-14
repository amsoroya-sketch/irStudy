#!/usr/bin/env python3
"""
OSCE & MCQ Topic Assessment + HEAL Image Integration System

This script:
1. Scans all OSCE and MCQ content files
2. Extracts topics and identifies those that would benefit from HEAL images
3. Maps topics to HEAL-available specialties
4. Downloads images using existing Playwright-based downloader
5. Creates linkage metadata between images and content

Usage:
    # Phase 1: Assess all content and create topic mapping
    python3 scripts/assess_and_link_heal_images.py --assess-only
    
    # Phase 2: Download images for matched topics
    python3 scripts/assess_and_link_heal_images.py --download-images --phase 1
    
    # Phase 3: Create full linkage metadata
    python3 scripts/assess_and_link_heal_images.py --create-linkages
    
    # Complete workflow
    python3 scripts/assess_and_link_heal_images.py --full-workflow
"""

import json
import re
import argparse
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import asyncio
import sys

# Import the existing HEAL downloader
sys.path.insert(0, str(Path(__file__).parent))
from download_heal_playwright import HEALPlaywrightDownloader, save_metadata

# ==========================================
# HEAL SPECIALTY COVERAGE (from HEAL_TOPIC_ANALYSIS.md)
# ==========================================

HEAL_AVAILABLE_SPECIALTIES = {
    # High coverage - excellent for AMC
    'hematology': {
        'coverage': 'exceptional',
        'items': 1500,
        'topics': [
            'acute myeloid leukemia', 'acute lymphoblastic leukemia', 'chronic myeloid leukemia',
            'chronic lymphocytic leukemia', 'sickle cell anemia', 'thalassemia', 'iron deficiency anemia',
            'megaloblastic anemia', 'hemolytic anemia', 'aplastic anemia', 'multiple myeloma',
            'lymphoma', 'disseminated intravascular coagulation', 'thrombocytopenia', 'hemophilia',
            'von willebrand disease', 'bone marrow', 'blood smear', 'blast cells', 'auer rods',
            'spherocytosis', 'elliptocytosis', 'target cells', 'schistocytes', 'rouleaux formation',
            'neutropenia', 'leukocytosis', 'infectious mononucleosis', 'atypical lymphocytes'
        ]
    },
    'dermatology': {
        'coverage': 'exceptional',
        'items': 330,
        'topics': [
            'melanoma', 'basal cell carcinoma', 'squamous cell carcinoma', 'atopic dermatitis',
            'eczema', 'contact dermatitis', 'seborrheic dermatitis', 'nummular dermatitis',
            'stasis dermatitis', 'psoriasis', 'lichen planus', 'pityriasis rosea', 'cellulitis',
            'erysipelas', 'impetigo', 'herpes zoster', 'herpes simplex', 'fungal infection',
            'tinea', 'urticaria', 'angioedema', 'drug eruption', 'stevens johnson syndrome',
            'acne vulgaris', 'acne rosacea', 'perioral dermatitis', 'vitiligo', 'alopecia areata',
            'pemphigus', 'bullous pemphigoid', 'scabies', 'molluscum contagiosum', 'warts',
            'seborrheic keratosis', 'skin tag', 'angioma', 'nevus', 'dermatofibroma'
        ]
    },
    'cardiology_ecg': {
        'coverage': 'exceptional',
        'items': 248,
        'topics': [
            'atrial fibrillation', 'atrial flutter', 'supraventricular tachycardia',
            'ventricular tachycardia', 'ventricular fibrillation', 'sinus tachycardia',
            'sinus bradycardia', 'premature atrial contraction', 'premature ventricular contraction',
            'left bundle branch block', 'right bundle branch block', 'first degree AV block',
            'second degree AV block', 'third degree AV block', 'bifascicular block',
            'myocardial infarction', 'STEMI', 'NSTEMI', 'anterior MI', 'inferior MI',
            'lateral MI', 'posterior MI', 'left ventricular hypertrophy', 'right ventricular hypertrophy',
            'left atrial enlargement', 'right atrial enlargement', 'pacemaker rhythm',
            'pericarditis', 'hyperkalemia ECG', 'hypokalemia ECG', 'long QT syndrome',
            'brugada syndrome', 'electrocardiogram', 'ECG interpretation'
        ]
    },
    
    # Good coverage
    'anatomy': {
        'coverage': 'excellent',
        'items': 690,
        'topics': [
            'heart anatomy', 'cardiac anatomy', 'lung anatomy', 'pulmonary anatomy',
            'brain anatomy', 'spinal cord', 'cranial nerves', 'brachial plexus',
            'liver anatomy', 'kidney anatomy', 'spleen anatomy', 'gastrointestinal anatomy',
            'shoulder anatomy', 'knee anatomy', 'hip anatomy', 'ankle anatomy',
            'skull anatomy', 'vertebral column', 'surface anatomy'
        ]
    },
    'respiratory': {
        'coverage': 'good',
        'items': 189,
        'topics': [
            'pneumonia', 'pulmonary edema', 'atelectasis', 'pneumothorax',
            'pleural effusion', 'lung nodule', 'COPD', 'emphysema', 'chronic bronchitis',
            'asthma', 'interstitial lung disease', 'pulmonary fibrosis', 'lung histology'
        ]
    },
    'pathology': {
        'coverage': 'good',
        'items': 108,
        'topics': [
            'adenocarcinoma', 'squamous cell carcinoma', 'lymphoma pathology',
            'carcinoma in situ', 'metastatic carcinoma', 'sarcoma', 'glioma',
            'meningioma', 'acute inflammation', 'chronic inflammation', 'granuloma',
            'abscess', 'necrosis', 'liver cirrhosis', 'fatty liver', 'kidney pathology'
        ]
    },
    'gastrointestinal': {
        'coverage': 'moderate',
        'items': 75,
        'topics': [
            'peptic ulcer', 'inflammatory bowel disease', 'crohn disease', 'ulcerative colitis',
            'colorectal cancer', 'gastroesophageal reflux', 'pancreatitis', 'hepatitis',
            'cholecystitis', 'appendicitis', 'GI histology'
        ]
    }
}

# Topics NOT available in HEAL (for exclusion)
HEAL_GAPS = [
    'neurology', 'psychiatry', 'obstetrics', 'gynecology', 'surgery',
    'emergency medicine', 'ophthalmology', ' ENT', 'orthopedics',
    'rheumatology', 'endocrinology', 'nephrology', 'radiology'
]

# ==========================================
# AMC EXAM TOPICS FROM OSCE/MCQ CONTENT
# ==========================================

OSCE_MEDICINE_TOPICS = [
    'chest pain', 'shortness of breath', 'palpitations', 'syncope', 'dizziness',
    'abdominal pain', 'GI bleeding', 'headache', 'weakness', 'limb examination',
    'thyroid examination', 'lymph node examination', 'ECG interpretation',
    'anaphylaxis', 'seizure', 'diabetes', 'dermatology examination'
]

OSCE_SURGERY_TOPICS = [
    'acute abdomen', 'surgical lumps', 'hernias', 'groin lump',
    'pre-operative assessment', 'post-operative assessment', 'trauma assessment'
]

OSCE_OBGYN_TOPICS = [
    'obstetric history', 'gynecological history', 'contraception counseling',
    'obstetric examination', 'gynecological examination', 'first trimester bleeding',
    'abnormal vaginal bleeding'
]

OSCE_PAEDIATRICS_TOPICS = [
    'paediatric history', 'common paediatric presentations', 'developmental assessment',
    'paediatric examination', 'parent communication'
]

OSCE_PSYCHIATRY_TOPICS = [
    'psychiatric history', 'mental state examination', 'risk assessment',
    'common psychiatric presentations', 'capacity assessment'
]

OSCE_ETHICS_COMMUNICATION_TOPICS = [
    'breaking bad news', 'communication skills', 'cultural variations',
    'emotional reactions', 'informed consent'
]

MCQ_SPECIALTIES = {
    'respiratory': ['asthma', 'COPD', 'pneumonia', 'pulmonary embolism', 'bronchiectasis',
                   'interstitial lung disease', 'lung cancer', 'pleural effusion', 'pneumothorax'],
    'cardiology': ['heart failure', 'coronary artery disease', 'arrhythmias', 'hypertension',
                  'valvular heart disease', 'cardiomyopathy', 'pericardial disease'],
    'gastroenterology': ['peptic ulcer', 'GERD', 'IBD', 'liver disease', 'pancreatitis',
                        'gastrointestinal bleeding', 'colorectal cancer'],
    'dermatology': ['eczema', 'psoriasis', 'acne', 'skin cancer', 'infections', 'blistering disorders'],
    'hematology': ['anemia', 'leukemia', 'lymphoma', 'coagulation disorders', 'thrombocytopenia'],
    'infectious_disease': ['sepsis', 'HIV', 'tuberculosis', 'endocarditis', 'meningitis'],
    'neurology': ['stroke', 'seizures', 'headache', 'multiple sclerosis', 'parkinson disease'],
    'endocrinology': ['diabetes', 'thyroid disorders', 'adrenal disorders', 'pituitary disorders'],
    'nephrology': ['CKD', 'AKI', 'nephrotic syndrome', 'glomerulonephritis'],
    'rheumatology': ['RA', 'SLE', 'vasculitis', 'spondyloarthritis', 'osteoarthritis'],
    'surgery': ['acute abdomen', 'trauma', 'surgical infections', 'hermias'],
    'ophthalmology': ['cataract', 'glaucoma', 'retinal disease', 'eye infections'],
    'ENT': ['otitis', 'sinusitis', 'tonsillitis', 'hearing loss'],
    'orthopedics': ['fractures', 'joint disorders', 'back pain', 'sports injuries'],
    'urology': ['UTI', 'kidney stones', 'prostate disorders', 'bladder cancer'],
    'obstetrics': ['prenatal care', 'labor', 'postpartum', 'pregnancy complications'],
    'gynecology': ['contraception', 'menstrual disorders', 'pelvic pain', 'cervical screening'],
    'pediatrics': ['development', 'common infections', 'genetic disorders', 'vaccination'],
    'psychiatry': ['depression', 'anxiety', 'psychosis', 'substance abuse', 'eating disorders'],
    'emergency_medicine': ['resuscitation', 'toxicology', 'environmental emergencies', 'trauma']
}


class TopicAssessor:
    """Assesses OSCE and MCQ topics for HEAL image compatibility"""
    
    def __init__(self):
        self.topic_mappings = defaultdict(list)
        self.heal_benefit_topics = []
        self.no_benefit_topics = []
        
    def assess_all_topics(self):
        """Assess all available topics from OSCE and MCQ content"""
        
        print("\n" + "="*70)
        print("ASSESSING ALL OSCE & MCQ TOPICS FOR HEAL IMAGE BENEFIT")
        print("="*70)
        
        # Combine all topics
        all_osce_topics = (
            OSCE_MEDICINE_TOPICS + OSCE_SURGERY_TOPICS + OSCE_OBGYN_TOPICS +
            OSCE_PAEDIATRICS_TOPICS + OSCE_PSYCHIATRY_TOPICS + OSCE_ETHICS_COMMUNICATION_TOPICS
        )
        
        all_mcq_topics = []
        for specialty, topics in MCQ_SPECIALTIES.items():
            all_mcq_topics.extend(topics)
        
        print(f"\nTotal OSCE topics: {len(all_osce_topics)}")
        print(f"Total MCQ topics: {len(all_mcq_topics)}")
        
        # Assess each topic
        for topic in all_osce_topics:
            self._assess_topic(topic, 'OSCE')
            
        for specialty, topics in MCQ_SPECIALTIES.items():
            for topic in topics:
                self._assess_topic(topic, f'MCQ-{specialty}')
        
        return self._generate_assessment_report()
    
    def _assess_topic(self, topic, source):
        """Assess a single topic for HEAL benefit"""
        
        topic_lower = topic.lower()
        matched = False
        
        # Check against HEAL available specialties
        for heal_specialty, data in HEAL_AVAILABLE_SPECIALTIES.items():
            # Direct match
            if topic_lower in heal_specialty.lower() or heal_specialty.lower() in topic_lower:
                self.topic_mappings[heal_specialty].append({
                    'topic': topic,
                    'source': source,
                    'match_type': 'direct'
                })
                matched = True
                break
            
            # Check sub-topics
            for sub_topic in data['topics']:
                if topic_lower in sub_topic.lower() or sub_topic.lower() in topic_lower:
                    self.topic_mappings[heal_specialty].append({
                        'topic': topic,
                        'source': source,
                        'match_type': 'sub_topic',
                        'heal_topic': sub_topic
                    })
                    matched = True
                    break
            
            if matched:
                break
        
        # Check against HEAL gaps (topics not available)
        if not matched:
            for gap in HEAL_GAPS:
                if gap.lower() in topic_lower or topic_lower in gap.lower():
                    self.no_benefit_topics.append({
                        'topic': topic,
                        'source': source,
                        'reason': f'Not available in HEAL - {gap}'
                    })
                    matched = True
                    break
        
        if not matched:
            self.no_benefit_topics.append({
                'topic': topic,
                'source': source,
                'reason': 'Not identified in HEAL database'
            })
    
    def _generate_assessment_report(self):
        """Generate comprehensive assessment report"""
        
        report = {
            'assessment_date': datetime.now().isoformat(),
            'summary': {
                'topics_with_heal_benefit': sum(len(v) for v in self.topic_mappings.values()),
                'topics_without_benefit': len(self.no_benefit_topics),
                'heal_specialties_matched': list(self.topic_mappings.keys())
            },
            'heal_benefit_mappings': dict(self.topic_mappings),
            'no_benefit_topics': self.no_benefit_topics,
            'recommendations': self._generate_recommendations()
        }
        
        return report
    
    def _generate_recommendations(self):
        """Generate recommendations based on assessment"""
        
        recommendations = []
        
        # Priority 1: High-yield dermatology
        if 'dermatology' in self.topic_mappings:
            dermatology_count = len(self.topic_mappings['dermatology'])
            recommendations.append({
                'priority': 1,
                'specialty': 'dermatology',
                'rationale': f'{dermatology_count} OSCE/MCQ topics would benefit from dermatology images',
                'heal_topics': ['eczema', 'psoriasis', 'melanoma', 'basal cell carcinoma', 
                              'cellulitis', 'herpes zoster', 'acne vulgaris'],
                'estimated_images': 50,
                'amc_value': 'Very High - dermatology cases appear in 50-60% of AMC exams'
            })
        
        # Priority 2: Hematology (blood smears)
        if 'hematology' in self.topic_mappings:
            hematology_count = len(self.topic_mappings['hematology'])
            recommendations.append({
                'priority': 2,
                'specialty': 'hematology',
                'rationale': f'{hematology_count} OSCE/MCQ topics would benefit from hematology images',
                'heal_topics': ['acute myeloid leukemia', 'sickle cell anemia', 'iron deficiency anemia',
                              'multiple myeloma', 'thrombocytopenia', 'blood smear morphology'],
                'estimated_images': 40,
                'amc_value': 'High - blood film interpretation tested in AMC'
            })
        
        # Priority 3: Cardiology ECG
        if 'cardiology_ecg' in self.topic_mappings:
            cardiology_count = len(self.topic_mappings['cardiology_ecg'])
            recommendations.append({
                'priority': 3,
                'specialty': 'cardiology_ecg',
                'rationale': f'{cardiology_count} OSCE/MCQ topics would benefit from ECG images',
                'heal_topics': ['atrial fibrillation', 'myocardial infarction', 'bundle branch block',
                              'ventricular tachycardia', 'left ventricular hypertrophy'],
                'estimated_images': 35,
                'amc_value': 'Very High - ECG interpretation critical for AMC'
            })
        
        # Priority 4: Anatomy
        if 'anatomy' in self.topic_mappings:
            recommendations.append({
                'priority': 4,
                'specialty': 'anatomy',
                'rationale': 'Physical examination stations benefit from anatomical images',
                'heal_topics': ['surface anatomy', 'heart anatomy', 'lung anatomy', 'cranial nerves'],
                'estimated_images': 25,
                'amc_value': 'Medium-High - supports physical examination understanding'
            })
        
        # Priority 5: Pathology
        if 'pathology' in self.topic_mappings:
            recommendations.append({
                'priority': 5,
                'specialty': 'pathology',
                'rationale': 'Histopathology images for disease understanding',
                'heal_topics': ['carcinoma', 'inflammation', 'lymphoma pathology'],
                'estimated_images': 20,
                'amc_value': 'Medium - supports disease mechanism understanding'
            })
        
        return recommendations


class HEALImageLinker:
    """Links downloaded HEAL images to OSCE/MCQ content"""
    
    def __init__(self, image_base_dir='data/medical_images/heal'):
        self.image_base_dir = Path(image_base_dir)
        self.linkages = []
        
    def create_linkage_metadata(self, assessment_report):
        """Create metadata linking images to OSCE/MCQ content"""
        
        print("\n" + "="*70)
        print("CREATING IMAGE-TO-CONTENT LINKAGES")
        print("="*70)
        
        for heal_specialty, mappings in assessment_report['heal_benefit_mappings'].items():
            specialty_dir = self.image_base_dir / heal_specialty
            
            if not specialty_dir.exists():
                print(f"  ⚠ Directory not found: {specialty_dir}")
                continue
            
            # Find all metadata files
            metadata_files = list(specialty_dir.glob('**/*_metadata.json'))
            
            for metadata_file in metadata_files:
                try:
                    with open(metadata_file, 'r') as f:
                        image_data = json.load(f)
                    
                    # Create linkages for each image
                    if isinstance(image_data, list):
                        for image in image_data:
                            self._create_image_linkage(image, mappings, heal_specialty)
                    
                except Exception as e:
                    print(f"  ✗ Error reading {metadata_file}: {e}")
        
        return self.linkages
    
    def _create_image_linkage(self, image, content_mappings, heal_specialty):
        """Create a linkage entry for a single image"""
        
        linkage = {
            'image_id': image.get('file_id'),
            'image_filename': image.get('filename'),
            'image_path': image.get('filepath'),
            'heal_specialty': heal_specialty,
            'title': image.get('title'),
            'description': image.get('description'),
            'subject': image.get('subject'),
            'heal_url': image.get('details_url'),
            'linked_content': content_mappings,
            'linkage_type': 'topic_match',
            'usage_recommendations': self._generate_usage_recommendations(
                heal_specialty, image.get('title', ''), image.get('description', '')
            )
        }
        
        self.linkages.append(linkage)
    
    def _generate_usage_recommendations(self, specialty, title, description):
        """Generate recommendations for how to use the image"""
        
        recommendations = []
        text = f"{title} {description}".lower()
        
        if specialty == 'dermatology':
            if any(x in text for x in ['eczema', 'dermatitis']):
                recommendations.append('Use in OSCE dermatology stations for atopic dermatitis cases')
                recommendations.append('MCQ: Identify eczema vs. other rashes')
            elif any(x in text for x in ['melanoma', 'carcinoma', 'skin cancer']):
                recommendations.append('Use in OSCE for skin cancer examination stations')
                recommendations.append('MCQ: ABCDE criteria for melanoma identification')
            elif any(x in text for x in ['psoriasis']):
                recommendations.append('OSCE: Psoriasis history and examination')
                recommendations.append('MCQ: Psoriasis management and complications')
            elif any(x in text for x in ['cellulitis', 'erysipelas']):
                recommendations.append('OSCE: Acute skin infection assessment')
                recommendations.append('MCQ: Cellulitis vs. DVT differentiation')
        
        elif specialty == 'hematology':
            if any(x in text for x in ['leukemia', 'blast']):
                recommendations.append('MCQ: Acute leukemia blood film interpretation')
                recommendations.append('OSCE: Discuss leukemia presentation with patient')
            elif any(x in text for x in ['anemia', 'sickle', 'thalassemia']):
                recommendations.append('MCQ: Anemia classification and blood smear findings')
            elif any(x in text for x in ['myeloma', 'myeloma']):
                recommendations.append('MCQ: Multiple myeloma diagnosis (CRAB features)')
        
        elif specialty == 'cardiology_ecg':
            if any(x in text for x in ['infarction', 'mi', 'ischemia']):
                recommendations.append('MCQ: STEMI vs. NSTEMI ECG changes')
                recommendations.append('MCQ: Localization of MI on ECG')
            elif any(x in text for x in ['fibrillation', 'flutter']):
                recommendations.append('MCQ: AF management and stroke risk (CHA2DS2-VASc)')
                recommendations.append('OSCE: Discuss AF diagnosis with patient')
            elif any(x in text for x in ['block', 'bundle']):
                recommendations.append('MCQ: Bundle branch block identification')
        
        return recommendations
    
    def save_linkages(self, output_file='data/heal_image_linkages.json'):
        """Save linkages to JSON file"""
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        linkage_report = {
            'created_date': datetime.now().isoformat(),
            'total_linkages': len(self.linkages),
            'linkages': self.linkages
        }
        
        with open(output_path, 'w') as f:
            json.dump(linkage_report, f, indent=2)
        
        print(f"\n✓ Linkages saved to: {output_path}")
        return output_path


class HEALDownloaderForContent:
    """Downloads HEAL images specifically for matched OSCE/MCQ topics"""
    
    def __init__(self):
        self.downloaded_images = []
        
    async def download_for_recommendations(self, recommendations, images_per_topic=10, 
                                          output_base='data/medical_images/heal'):
        """Download images based on assessment recommendations"""
        
        print("\n" + "="*70)
        print("DOWNLOADING HEAL IMAGES FOR OSCE/MCQ CONTENT")
        print("="*70)
        
        for rec in sorted(recommendations, key=lambda x: x['priority']):
            specialty = rec['specialty']
            heal_topics = rec['heal_topics']
            
            print(f"\n{'='*70}")
            print(f"Specialty: {specialty.upper()}")
            print(f"Priority: {rec['priority']}")
            print(f"AMC Value: {rec['amc_value']}")
            print(f"{'='*70}")
            
            specialty_images = []
            
            for topic in heal_topics:
                print(f"\n  Searching: {topic}")
                
                try:
                    downloader = HEALPlaywrightDownloader(headless=True)
                    
                    # Search and download
                    results = await downloader.search_and_extract_ids(topic, max_results=images_per_topic)
                    
                    if results:
                        # Create topic-specific folder
                        topic_folder = topic.replace(' ', '_').replace('/', '_')
                        output_dir = Path(output_base) / specialty / topic_folder
                        output_dir.mkdir(parents=True, exist_ok=True)
                        
                        # Download images
                        downloaded = await downloader.download_images(results, output_dir)
                        
                        if downloaded:
                            # Save metadata
                            save_metadata(downloaded, output_dir, topic_folder)
                            
                            print(f"    ✓ Downloaded {len(downloaded)} images")
                            specialty_images.extend(downloaded)
                            
                            # Rate limiting
                            await asyncio.sleep(2)
                        else:
                            print(f"    ⚠ No images downloaded for {topic}")
                    else:
                        print(f"    ⚠ No results found for {topic}")
                
                except Exception as e:
                    print(f"    ✗ Error downloading {topic}: {e}")
            
            self.downloaded_images.extend(specialty_images)
            print(f"\n  ✓ {specialty}: {len(specialty_images)} images downloaded")
        
        return self.downloaded_images


def print_assessment_summary(report):
    """Print a formatted assessment summary"""
    
    print("\n" + "="*70)
    print("ASSESSMENT SUMMARY")
    print("="*70)
    
    print(f"\n📊 Statistics:")
    print(f"  Topics with HEAL benefit: {report['summary']['topics_with_heal_benefit']}")
    print(f"  Topics without benefit: {report['summary']['topics_without_benefit']}")
    print(f"  HEAL specialties matched: {len(report['summary']['heal_specialties_matched'])}")
    
    print(f"\n✅ Topics that would BENEFIT from HEAL images:")
    for specialty, mappings in report['heal_benefit_mappings'].items():
        print(f"\n  {specialty.upper()} ({len(mappings)} topics):")
        for m in mappings[:5]:  # Show first 5
            print(f"    • {m['topic']} ({m['source']})")
        if len(mappings) > 5:
            print(f"    ... and {len(mappings) - 5} more")
    
    print(f"\n❌ Topics with NO HEAL benefit:")
    for item in report['no_benefit_topics'][:10]:
        print(f"    • {item['topic']} ({item['source']}) - {item['reason']}")
    if len(report['no_benefit_topics']) > 10:
        print(f"    ... and {len(report['no_benefit_topics']) - 10} more")
    
    print(f"\n🎯 RECOMMENDED DOWNLOAD PRIORITIES:")
    for rec in report['recommendations']:
        print(f"\n  Priority {rec['priority']}: {rec['specialty'].upper()}")
        print(f"    Rationale: {rec['rationale']}")
        print(f"    AMC Value: {rec['amc_value']}")
        print(f"    Estimated images: {rec['estimated_images']}")
        print(f"    HEAL topics: {', '.join(rec['heal_topics'][:5])}")


async def main():
    parser = argparse.ArgumentParser(
        description='Assess OSCE/MCQ topics and download HEAL images',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Assess only (no download)
  python3 scripts/assess_and_link_heal_images.py --assess-only
  
  # Download images for assessed topics
  python3 scripts/assess_and_link_heal_images.py --download-images
  
  # Full workflow: assess + download + create linkages
  python3 scripts/assess_and_link_heal_images.py --full-workflow
        '''
    )
    
    parser.add_argument('--assess-only', action='store_true',
                       help='Only assess topics, do not download')
    parser.add_argument('--download-images', action='store_true',
                       help='Download images for matched topics')
    parser.add_argument('--create-linkages', action='store_true',
                       help='Create linkage metadata')
    parser.add_argument('--full-workflow', action='store_true',
                       help='Run complete workflow')
    parser.add_argument('--images-per-topic', type=int, default=10,
                       help='Images to download per topic (default: 10)')
    parser.add_argument('--output-dir', default='data/medical_images/heal',
                       help='Output directory for images')
    parser.add_argument('--assessment-file', default='data/heal_topic_assessment.json',
                       help='File to save assessment report')
    
    args = parser.parse_args()
    
    # Default to assess-only if no action specified
    if not any([args.assess_only, args.download_images, args.create_linkages, args.full_workflow]):
        args.assess_only = True
    
    # Full workflow enables all steps
    if args.full_workflow:
        args.assess_only = True
        args.download_images = True
        args.create_linkages = True
    
    assessment_report = None
    
    # Step 1: Assess topics
    if args.assess_only or args.full_workflow:
        assessor = TopicAssessor()
        assessment_report = assessor.assess_all_topics()
        
        # Print summary
        print_assessment_summary(assessment_report)
        
        # Save assessment
        Path(args.assessment_file).parent.mkdir(parents=True, exist_ok=True)
        with open(args.assessment_file, 'w') as f:
            json.dump(assessment_report, f, indent=2)
        print(f"\n✓ Assessment saved to: {args.assessment_file}")
    
    # Step 2: Download images
    if args.download_images:
        if assessment_report is None:
            # Load existing assessment
            try:
                with open(args.assessment_file, 'r') as f:
                    assessment_report = json.load(f)
            except FileNotFoundError:
                print(f"✗ Assessment file not found: {args.assessment_file}")
                print("  Run with --assess-only first")
                return
        
        downloader = HEALDownloaderForContent()
        downloaded = await downloader.download_for_recommendations(
            assessment_report['recommendations'],
            images_per_topic=args.images_per_topic,
            output_base=args.output_dir
        )
        
        print(f"\n{'='*70}")
        print(f"DOWNLOAD COMPLETE: {len(downloaded)} images")
        print(f"{'='*70}")
    
    # Step 3: Create linkages
    if args.create_linkages:
        if assessment_report is None:
            try:
                with open(args.assessment_file, 'r') as f:
                    assessment_report = json.load(f)
            except FileNotFoundError:
                print(f"✗ Assessment file not found: {args.assessment_file}")
                return
        
        linker = HEALImageLinker(args.output_dir)
        linkages = linker.create_linkage_metadata(assessment_report)
        linker.save_linkages()
        
        print(f"\n✓ Created {len(linkages)} image-content linkages")


if __name__ == '__main__':
    asyncio.run(main())
