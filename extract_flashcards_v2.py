#!/usr/bin/env python3
"""
ICRP OSCE Flashcard Extractor v2
Simplified version with better control over card distribution
"""

import json
import re
import os
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict

class FlashcardExtractor:
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.cards = []
        self.card_id = 1

        # Target distribution (total 750 cards)
        self.targets = {
            'red_flags': 150,
            'differentials': 200,
            'physical_exam': 150,
            'communication': 100,
            'australian_context': 50,
            'img_mistakes': 100
        }

        self.counts = {k: 0 for k in self.targets.keys()}
        self.seen = set()

    def clean_text(self, text: str) -> str:
        """Clean extracted text"""
        text = ' '.join(text.split())
        text = text.replace('\u2019', "'").replace('\u201c', '"').replace('\u201d', '"')
        return text[:500]  # Limit length

    def add_card(self, category, front, back, deck, tags, source, difficulty='medium'):
        """Add card if not duplicate and under limit"""
        if self.counts[category] >= self.targets[category]:
            return False

        front_key = front.lower().strip()
        if front_key in self.seen:
            return False

        self.cards.append({
            'id': self.card_id,
            'front': self.clean_text(front),
            'back': self.clean_text(back),
            'deck': deck,
            'tags': tags,
            'source': source,
            'difficulty': difficulty,
            'category': category
        })

        self.seen.add(front_key)
        self.counts[category] += 1
        self.card_id += 1
        return True

    def get_deck(self, file_path: Path) -> str:
        """Determine deck from file path"""
        parts = file_path.parts

        if 'Medicine' in parts:
            fn = file_path.stem
            if any(x in fn for x in ['GI', 'Abdominal', 'Bleeding']):
                return 'Medicine_Gastroenterology'
            elif any(x in fn for x in ['Cardiovascular', 'Respiratory']):
                return 'Medicine_Cardiorespiratory'
            elif any(x in fn for x in ['Neurology', 'Neuro', 'Headache', 'Weakness']):
                return 'Medicine_Neurology'
            elif any(x in fn for x in ['Endocrinology', 'Diabetes']):
                return 'Medicine_Endocrinology'
            elif any(x in fn for x in ['Emergency', 'Anaphylaxis', 'Seizure']):
                return 'Medicine_Emergency'
            elif 'ECG' in fn:
                return 'Medicine_ECG'
            else:
                return 'Medicine_General'
        elif 'Surgery' in parts:
            return 'Surgery'
        elif 'ObGyn' in parts:
            return 'ObGyn'
        elif 'Paediatrics' in parts:
            return 'Paediatrics'
        elif 'Psychiatry' in parts:
            return 'Psychiatry'
        elif 'Ethics_Communication' in parts or 'Mock_Stations' in parts:
            return 'Ethics_Communication'
        return 'General'

    def extract_red_flags(self, text, file_path):
        """Extract red flag cards"""
        deck = self.get_deck(file_path)

        # Pattern: 🚨 markers or "RED FLAG" text
        patterns = [
            r'🚨+\s*([^🚨\n]{20,200})',
            r'RED FLAG[:\s]+([^\n]{20,200})',
            r'CRITICAL[:\s]+([^\n]{20,200})',
            r'MUST NOT MISS[:\s]+([^\n]{20,200})',
        ]

        for pattern in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                rf_text = match.group(1).strip()

                # Get context (500 chars after)
                context_end = min(len(text), match.end() + 500)
                context = text[match.end():context_end]

                # Try to extract explanation
                exp_match = re.search(r'^[:\s]*(.+?)(?:\n\n|\n[A-Z]{2,})', context, re.DOTALL)
                explanation = exp_match.group(1).strip() if exp_match else "Requires immediate recognition and action"

                self.add_card(
                    'red_flags',
                    f"🚨 RED FLAG: {rf_text}",
                    explanation,
                    deck,
                    ['red-flag', 'critical'],
                    file_path.name,
                    'hard'
                )

    def extract_differentials(self, text, file_path):
        """Extract differential diagnosis cards"""
        deck = self.get_deck(file_path)

        # Pattern: "Differential diagnosis" or "Causes of X"
        patterns = [
            (r'Differential\s+Diagnosis[:\s]*(.+?)(?:\n\n|\n[A-Z][A-Z]|\Z)', 'Differential diagnosis'),
            (r'Immediate\s+Differential[:\s]*(.+?)(?:\n\n|\n[A-Z][A-Z]|\Z)', 'Immediate differentials'),
            (r'Causes?\s+of\s+([^:\n]{5,80})[:\s]*(.+?)(?:\n\n|\n[A-Z][A-Z]|\Z)', None),
            (r'Differentials?[:\s]+(.+?)(?:\n\n|\n[A-Z][A-Z]|\Z)', 'Differentials'),
            (r'Common\s+causes[:\s]+(.+?)(?:\n\n|\n[A-Z][A-Z]|\Z)', 'Common causes'),
        ]

        for pattern, default_front in patterns:
            for match in re.finditer(pattern, text, re.DOTALL | re.IGNORECASE):
                if default_front:
                    front = default_front
                    causes_text = match.group(1)
                else:
                    # Causes of X pattern
                    front = f"What are the causes of: {match.group(1).strip()}?"
                    causes_text = match.group(2)

                # Extract bullet points or numbered items
                bullets = re.findall(r'(?:[-•]|\d+\.)\s*([^\n]{10,150})', causes_text)

                if len(bullets) >= 2:  # Lowered from 3 to 2
                    back = '\n'.join([f"• {b.strip()}" for b in bullets[:12]])
                    self.add_card(
                        'differentials',
                        front,
                        back,
                        deck,
                        ['differential', 'diagnosis'],
                        file_path.name
                    )
                    break  # One per pattern match

    def extract_physical_exam(self, text, file_path):
        """Extract physical exam technique cards"""
        deck = self.get_deck(file_path)

        # Pattern 1: "5 Ps" framework
        if '5 Ps' in text or '5 P\'s' in text or '5Ps' in text:
            match = re.search(r'5\s*P[s\']*[:\s]+(.+?)(?:\n\n[A-Z]|\Z)', text, re.DOTALL | re.IGNORECASE)
            if match:
                ps_text = match.group(1)
                ps_items = re.findall(r'([A-Z][^:\n]+?):\s*([^\n]+)', ps_text)

                if len(ps_items) >= 4:  # Lowered from 5
                    self.add_card(
                        'physical_exam',
                        "What are the 5 Ps in vascular examination?",
                        '\n'.join([f"• {p[0]}: {p[1]}" for p in ps_items[:6]]),
                        deck,
                        ['physical-exam', '5-ps'],
                        file_path.name
                    )

        # Pattern 2: Examination steps (IPPA)
        for step in ['Inspection', 'Palpation', 'Percussion', 'Auscultation']:
            pattern = rf'{step}[:\s]+(.+?)(?:\n\n|\n(?:Palpation|Percussion|Auscultation|Inspection|[A-Z]{{2,}})|\Z)'
            matches = re.finditer(pattern, text, re.DOTALL | re.IGNORECASE)

            for match in matches:
                step_text = match.group(1).strip()

                # Extract bullet points or numbered items
                items = re.findall(r'(?:[-•]|\d+\.)\s*([^\n]{10,120})', step_text)

                if len(items) >= 2:
                    self.add_card(
                        'physical_exam',
                        f"Physical examination - {step}",
                        '\n'.join([f"• {item}" for item in items[:10]]),
                        deck,
                        ['physical-exam', 'technique', step.lower()],
                        file_path.name
                    )
                    break  # One per step per file

        # Pattern 3: General examination sequences
        seq_patterns = [
            r'Examination\s+[Ss]equence[:\s]+(.+?)(?:\n\n|\Z)',
            r'Systematic\s+[Ee]xamination[:\s]+(.+?)(?:\n\n|\Z)',
            r'Examination\s+[Ss]teps[:\s]+(.+?)(?:\n\n|\Z)',
        ]

        for pattern in seq_patterns:
            match = re.search(pattern, text, re.DOTALL)
            if match:
                seq_text = match.group(1)
                steps = re.findall(r'(?:[-•]|\d+\.)\s*([^\n]{10,120})', seq_text)

                if len(steps) >= 3:
                    self.add_card(
                        'physical_exam',
                        f"Examination sequence ({file_path.stem})",
                        '\n'.join([f"{i+1}. {s}" for i, s in enumerate(steps[:10])]),
                        deck,
                        ['physical-exam', 'sequence'],
                        file_path.name
                    )
                    break  # One sequence per file

    def extract_communication(self, text, file_path):
        """Extract communication phrases"""
        deck = self.get_deck(file_path)

        # SPIKES framework
        if 'SPIKES' in text:
            self.add_card(
                'communication',
                "What does SPIKES stand for (breaking bad news)?",
                "S - Setting up\nP - Perception\nI - Invitation\nK - Knowledge\nE - Empathy\nS - Strategy and Summary",
                deck,
                ['communication', 'spikes', 'framework'],
                file_path.name,
                'easy'
            )

        # "What to say" phrases
        phrase_patterns = [
            r'"([^"]{30,180})"',
            r'Say[:\s]+"([^"]+)"',
        ]

        for pattern in phrase_patterns:
            for match in re.finditer(pattern, text):
                phrase = match.group(1).strip()

                # Check if it's a communication phrase (has pronouns, empathetic language)
                if any(word in phrase.lower() for word in ['you', 'i', 'we', 'your', 'understand', 'feel', 'sorry']):
                    self.add_card(
                        'communication',
                        f"Communication phrase",
                        phrase,
                        deck,
                        ['communication', 'phrase'],
                        file_path.name,
                        'easy'
                    )

    def extract_australian(self, text, file_path):
        """Extract Australian context"""
        deck = self.get_deck(file_path)

        # eTG references
        etg_matches = re.finditer(r'eTG\s+\d{4}[:\s]+([^\n]{30,250})', text)
        for match in etg_matches:
            self.add_card(
                'australian_context',
                "Australian guideline (eTG)",
                match.group(1).strip(),
                deck,
                ['australian', 'etg'],
                file_path.name
            )

        # PBS references
        pbs_matches = re.finditer(r'PBS[:\s]+([^\n]{30,200})', text)
        for match in pbs_matches:
            self.add_card(
                'australian_context',
                "PBS information",
                match.group(1).strip(),
                deck,
                ['australian', 'pbs'],
                file_path.name
            )

    def extract_img_mistakes(self, text, file_path):
        """Extract IMG mistakes"""
        deck = self.get_deck(file_path)

        # "Common IMG Mistakes" sections
        mistake_sections = re.finditer(
            r'Common\s+IMG\s+Mistake[s]?[:\s]+(.+?)(?:\n\n[A-Z]|\Z)',
            text,
            re.DOTALL | re.IGNORECASE
        )

        for section in mistake_sections:
            mistakes = re.findall(r'\d+\.\s+([^\n]{20,250})', section.group(1))

            for mistake in mistakes:
                # Split on colon if present (mistake: explanation)
                if ':' in mistake:
                    parts = mistake.split(':', 1)
                    front = f"IMG Mistake: {parts[0].strip()}"
                    back = parts[1].strip()
                else:
                    front = "Common IMG mistake to avoid"
                    back = mistake

                self.add_card(
                    'img_mistakes',
                    front,
                    back,
                    deck,
                    ['img-mistake', 'avoid'],
                    file_path.name
                )

        # Standalone mistakes
        for pattern in [r'❌\s+([^\n]{20,200})', r'AVOID[:\s]+([^\n]{20,200})', r'Never\s+([^\n]{20,200})']:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                self.add_card(
                    'img_mistakes',
                    "What should you AVOID?",
                    match.group(1).strip(),
                    deck,
                    ['img-mistake'],
                    file_path.name
                )

    def process_file(self, file_path: Path):
        """Process single HTML file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            html = f.read()

        soup = BeautifulSoup(html, 'html.parser')

        # Remove scripts and styles
        for tag in soup(['script', 'style']):
            tag.decompose()

        text = soup.get_text()

        before = len(self.cards)

        self.extract_red_flags(text, file_path)
        self.extract_differentials(text, file_path)
        self.extract_physical_exam(text, file_path)
        self.extract_communication(text, file_path)
        self.extract_australian(text, file_path)
        self.extract_img_mistakes(text, file_path)

        added = len(self.cards) - before
        print(f"{file_path.name}: +{added} cards")

    def process_all(self):
        """Process all HTML files"""
        files = list(self.base_dir.glob('**/*.html'))
        files = [f for f in files if f.stem not in ['00_MASTER_INDEX_AMC_CLINICAL_OSCE', 'START_HERE']]

        print(f"Processing {len(files)} files...\n")

        for file_path in sorted(files):
            self.process_file(file_path)

        print(f"\n{'='*60}")
        print(f"Total cards: {len(self.cards)}")
        for cat, count in sorted(self.counts.items()):
            target = self.targets[cat]
            pct = (count / target * 100) if target > 0 else 0
            print(f"  {cat}: {count}/{target} ({pct:.0f}%)")

    def save(self, output_path: Path):
        """Save to JSON"""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            'metadata': {
                'version': '1.0',
                'created': datetime.now().isoformat(),
                'total_cards': len(self.cards),
                'by_category': self.counts,
                'targets': self.targets
            },
            'cards': self.cards
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"\nSaved to: {output_path}")


def main():
    extractor = FlashcardExtractor('/home/dev/Development/irStudy/ICRP_OSCE_Preparation')
    extractor.process_all()
    extractor.save(Path('/home/dev/Development/irStudy/ICRP_Program_Resources/Flashcards/flashcard_data.json'))


if __name__ == '__main__':
    main()
