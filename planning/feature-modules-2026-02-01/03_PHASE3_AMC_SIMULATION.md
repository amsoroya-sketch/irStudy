# Phase 3: AMC Clinical Exam Simulation
**Owner:** AI/ML Engineer + Full-Stack Developer
**Duration:** 150-200 hours (6 weeks full-time, 12 weeks part-time)
**Priority:** P1 (High - Core exam preparation feature)
**Status:** Ready to Start (after Phase 2)

---

## 📋 Overview

This phase builds the **most advanced feature**: An AI-powered AMC Clinical Examination simulator with:
- **AI Patient**: Conversational agent with emotional states (Claude 3.5 Sonnet + voice synthesis)
- **AI Examiner**: Real-time scoring using 15-mark rubrics from 150+ OSCEs
- **WebRTC Interface**: Browser-based video/audio for realistic exam simulation
- **Hybrid Mode**: Untimed practice mode + timed exam mode (8 minutes per station)

**Key Achievement:** 90%+ realism score + ±2 mark scoring accuracy vs. human examiners

---

## 🎯 Goals

1. **AI Patient Agent** (40 hours)
   - LangChain conversational agent
   - Claude 3.5 Sonnet roleplay
   - Patient script parsing (from OSCE JSON files)
   - Emotional state management (tearful, anxious, angry, etc.)
   - Memory of conversation history

2. **AI Examiner Scoring** (30 hours)
   - Rubric-based scoring (15-mark stations)
   - Real-time marking during conversation
   - Feedback generation (strengths/weaknesses)
   - Pass/fail determination (9/15 threshold)

3. **WebRTC Frontend** (40 hours)
   - React video/audio components
   - useWebRTC custom hook
   - Patient video display (avatar or AI-generated)
   - Audio recording for transcript
   - Session management

4. **Text-to-Speech** (15 hours)
   - ElevenLabs integration
   - Australian accent voice selection
   - Emotional voice synthesis (tearful, anxious)
   - Low-latency streaming

5. **Speech-to-Text** (15 hours)
   - OpenAI Whisper integration
   - Real-time transcription
   - Conversation logging
   - Medical terminology accuracy

6. **Real-time Scoring UI** (20 hours)
   - Live rubric display
   - Mark allocation visualization
   - Instant feedback panel
   - Performance analytics

7. **Testing & Quality Assurance** (30 hours)
   - AI patient quality testing (50 OSCEs)
   - Scoring accuracy validation
   - WebRTC reliability testing
   - User acceptance testing

---

## ✅ Prerequisites

- [x] Phase 1 completed (React architecture)
- [x] Phase 2 completed (Validation agents)
- [x] 150+ OSCE files in `/home/dev/Development/irStudy/data/osces/`
- [x] Claude 3.5 Sonnet API access
- [x] ElevenLabs API account
- [x] OpenAI Whisper API access

---

## 📝 Detailed Task Breakdown

### Task 1: AI Patient Agent (40 hours)

**Priority:** P0 (CRITICAL - core simulation feature)

**Setup Project:**

```bash
cd /home/dev/Development/irStudy
mkdir -p amc-simulation
cd amc-simulation

# Backend setup
mkdir -p backend
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
cat > requirements.txt << 'EOF'
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.0
anthropic==0.8.0
langchain==0.1.0
langchain-anthropic==0.1.0
python-jose[cryptography]==3.3.0
python-multipart==0.0.6
websockets==12.0
httpx==0.26.0
python-dotenv==1.0.0
sqlalchemy==2.0.23
openai==1.6.0
elevenlabs==0.2.26
EOF

pip install -r requirements.txt

# Create directory structure
mkdir -p {agents,api,models,schemas,services,utils}
mkdir -p api/routes
```

**Load OSCE Data:**

```python
# backend/utils/osce_loader.py
import json
import os
from typing import List, Dict
from pathlib import Path

class OSCELoader:
    """Load and parse OSCE scenarios for AI patient simulation"""

    def __init__(self, osce_dir: str = "/home/dev/Development/irStudy/data/osces"):
        self.osce_dir = Path(osce_dir)
        self.osces = self._load_all_osces()

    def _load_all_osces(self) -> List[Dict]:
        """Load all OSCE JSON files"""
        osces = []

        for file_path in self.osce_dir.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    # Handle both single OSCE and array of OSCEs
                    if isinstance(data, list):
                        osces.extend(data)
                    else:
                        osces.append(data)
            except Exception as e:
                print(f"Error loading {file_path}: {e}")

        return osces

    def get_osce_by_id(self, osce_id: str) -> Dict:
        """Get specific OSCE by ID"""
        for osce in self.osces:
            if osce.get('id') == osce_id:
                return osce
        raise ValueError(f"OSCE {osce_id} not found")

    def get_random_osce(self, topic: str = None) -> Dict:
        """Get random OSCE, optionally filtered by topic"""
        import random

        filtered_osces = self.osces
        if topic:
            filtered_osces = [o for o in self.osces if topic.lower() in o.get('topic', '').lower()]

        if not filtered_osces:
            raise ValueError(f"No OSCEs found for topic: {topic}")

        return random.choice(filtered_osces)

    def get_patient_script(self, osce: Dict) -> Dict:
        """Extract patient roleplay script from OSCE"""
        return {
            'name': osce.get('patient_name', 'Patient'),
            'age': osce.get('patient_age', 45),
            'gender': osce.get('patient_gender', 'Unknown'),
            'presenting_complaint': osce.get('presenting_complaint', ''),
            'history': osce.get('history_details', {}),
            'emotional_state': osce.get('emotional_state', 'neutral'),
            'key_information': osce.get('key_information_to_disclose', []),
            'concerns': osce.get('patient_concerns', []),
            'background_context': osce.get('background_context', ''),
        }

    def get_rubric(self, osce: Dict) -> Dict:
        """Extract marking rubric from OSCE"""
        return {
            'total_marks': osce.get('total_marks', 15),
            'pass_mark': osce.get('pass_mark', 9),
            'criteria': osce.get('marking_criteria', []),
            'key_skills': osce.get('key_skills_assessed', []),
        }
```

**AI Patient Agent (LangChain + Claude):**

```python
# backend/agents/ai_patient_agent.py
from langchain.chat_models import ChatAnthropic
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain.memory import ConversationBufferMemory
from typing import List, Dict
import os

class AIPatientAgent:
    """
    AI Patient Agent using Claude 3.5 Sonnet for realistic OSCE simulation.

    Features:
    - Stays in character throughout conversation
    - Manages emotional states (tearful, anxious, angry, etc.)
    - Reveals information progressively (not all at once)
    - Responds realistically to student's questions and empathy
    """

    def __init__(self, patient_script: Dict, emotional_state: str = 'neutral'):
        self.patient_script = patient_script
        self.emotional_state = emotional_state
        self.memory = ConversationBufferMemory(return_messages=True)

        # Initialize Claude 3.5 Sonnet
        self.llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            temperature=0.7,  # Higher temperature for more natural conversation
            max_tokens=500,   # Limit response length (patients don't monologue)
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
        )

        self.system_prompt = self._build_system_prompt()

    def _build_system_prompt(self) -> str:
        """Construct system prompt for AI patient roleplay"""
        emotional_instructions = {
            'tearful': "You are tearful and emotional. Pause to cry occasionally. Show vulnerability.",
            'anxious': "You are anxious and worried. Speak quickly, interrupt yourself, ask for reassurance.",
            'angry': "You are frustrated and angry. Be defensive initially, but may soften with empathy.",
            'neutral': "You are calm and cooperative, answering questions clearly.",
            'confused': "You are confused and forgetful. Give vague or contradictory information sometimes.",
            'defensive': "You are defensive and reluctant to share. Need to build trust first."
        }

        emotional_instruction = emotional_instructions.get(self.emotional_state, emotional_instructions['neutral'])

        return f"""You are a patient in a medical consultation. Your role is to realistically portray this patient scenario for an AMC Clinical Examination.

PATIENT DETAILS:
- Name: {self.patient_script['name']}
- Age: {self.patient_script['age']}
- Gender: {self.patient_script['gender']}
- Presenting Complaint: {self.patient_script['presenting_complaint']}

BACKGROUND CONTEXT:
{self.patient_script['background_context']}

EMOTIONAL STATE:
{emotional_instruction}

KEY INFORMATION TO DISCLOSE (reveal naturally when asked appropriate questions):
{chr(10).join('- ' + info for info in self.patient_script['key_information'])}

PATIENT CONCERNS:
{chr(10).join('- ' + concern for concern in self.patient_script['concerns'])}

ROLEPLAY INSTRUCTIONS:
1. Stay in character - you are NOT an AI, you are this patient
2. Respond naturally and conversationally (1-3 sentences typically)
3. Do NOT volunteer all information immediately - wait for questions
4. Show appropriate emotions (use pauses like "..." when emotional)
5. Be realistic - patients sometimes forget details, get confused, or need clarification
6. Respond positively to empathy (e.g., "I can see this is difficult for you")
7. Do NOT break character or mention you are roleplaying
8. Use Australian English (e.g., "GP" not "PCP", "theatre" not "OR")

IMPORTANT:
- Answer the student's questions, but don't give away everything at once
- If asked about something not in your script, improvise reasonably based on the scenario
- If the student shows empathy or good communication skills, respond warmly
- If rushed or interrupted, you may become less cooperative

Begin the consultation naturally when the student greets you or asks how you can be helped."""

    async def respond(self, student_message: str) -> str:
        """
        Generate AI patient response to student's question/statement.

        Args:
            student_message: What the medical student said

        Returns:
            AI patient's response (1-3 sentences typically)
        """
        # Add student message to memory
        self.memory.chat_memory.add_user_message(student_message)

        # Build full conversation history
        messages = [SystemMessage(content=self.system_prompt)]

        # Add conversation history
        for msg in self.memory.chat_memory.messages:
            if isinstance(msg, HumanMessage):
                messages.append(HumanMessage(content=msg.content))
            elif isinstance(msg, AIMessage):
                messages.append(AIMessage(content=msg.content))

        # Get AI response
        response = await self.llm.ainvoke(messages)
        response_text = response.content

        # Add AI response to memory
        self.memory.chat_memory.add_ai_message(response_text)

        return response_text

    def update_emotional_state(self, new_state: str):
        """Update patient's emotional state during conversation"""
        self.emotional_state = new_state
        # System prompt will be regenerated on next response

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get full conversation history"""
        history = []
        for msg in self.memory.chat_memory.messages:
            if isinstance(msg, HumanMessage):
                history.append({"role": "student", "content": msg.content})
            elif isinstance(msg, AIMessage):
                history.append({"role": "patient", "content": msg.content})
        return history

    def reset(self):
        """Reset conversation memory"""
        self.memory.clear()
```

**Test AI Patient:**

```python
# backend/tests/test_ai_patient.py
import asyncio
from agents.ai_patient_agent import AIPatientAgent
from utils.osce_loader import OSCELoader

async def test_ai_patient():
    # Load OSCE
    loader = OSCELoader()
    osce = loader.get_random_osce(topic="respiratory")
    patient_script = loader.get_patient_script(osce)

    # Create AI patient
    patient = AIPatientAgent(patient_script, emotional_state='anxious')

    # Simulate conversation
    student_messages = [
        "Hello, I'm Dr. Smith. How can I help you today?",
        "How long have you been experiencing this cough?",
        "Is the cough productive? Are you bringing up any sputum?",
        "Have you had any fevers or night sweats?",
        "I can see this is worrying for you. We'll get to the bottom of this.",
    ]

    print(f"\n{'='*60}")
    print(f"OSCE: {osce.get('title', 'Untitled')}")
    print(f"Patient: {patient_script['name']}, {patient_script['age']}, {patient_script['gender']}")
    print(f"Emotional State: {patient.emotional_state}")
    print(f"{'='*60}\n")

    for msg in student_messages:
        print(f"Student: {msg}")
        response = await patient.respond(msg)
        print(f"Patient: {response}\n")

    # Print full conversation
    print(f"\n{'='*60}")
    print("FULL CONVERSATION HISTORY:")
    print(f"{'='*60}")
    for turn in patient.get_conversation_history():
        print(f"{turn['role'].upper()}: {turn['content']}")

if __name__ == "__main__":
    asyncio.run(test_ai_patient())
```

**API Endpoint for AI Patient:**

```python
# backend/api/routes/ai_patient.py
from fastapi import APIRouter, HTTPException, WebSocket
from pydantic import BaseModel
from agents.ai_patient_agent import AIPatientAgent
from utils.osce_loader import OSCELoader
import json

router = APIRouter(prefix="/api/ai-patient", tags=["ai-patient"])

# Global store for active patient agents (in production, use Redis)
active_patients = {}

class StartSessionRequest(BaseModel):
    osce_id: str
    emotional_state: str = 'neutral'

class ChatRequest(BaseModel):
    session_id: str
    message: str

@router.post("/start")
async def start_patient_session(request: StartSessionRequest):
    """Start new AI patient session"""
    try:
        # Load OSCE
        loader = OSCELoader()
        osce = loader.get_osce_by_id(request.osce_id)
        patient_script = loader.get_patient_script(osce)

        # Create session ID
        import uuid
        session_id = f"patient_{uuid.uuid4().hex[:8]}"

        # Create AI patient
        patient = AIPatientAgent(patient_script, request.emotional_state)

        # Store in active sessions
        active_patients[session_id] = patient

        return {
            "session_id": session_id,
            "patient_name": patient_script['name'],
            "presenting_complaint": patient_script['presenting_complaint'],
            "emotional_state": request.emotional_state,
            "osce_title": osce.get('title', 'Untitled')
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/chat")
async def chat_with_patient(request: ChatRequest):
    """Send message to AI patient and get response"""
    if request.session_id not in active_patients:
        raise HTTPException(status_code=404, detail="Session not found")

    patient = active_patients[request.session_id]

    try:
        response = await patient.respond(request.message)
        return {
            "response": response,
            "conversation_history": patient.get_conversation_history()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.websocket("/ws/{session_id}")
async def websocket_patient_chat(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time chat"""
    await websocket.accept()

    if session_id not in active_patients:
        await websocket.send_json({"error": "Session not found"})
        await websocket.close()
        return

    patient = active_patients[session_id]

    try:
        while True:
            # Receive message from student
            data = await websocket.receive_text()
            message = json.loads(data)

            # Get AI patient response
            response = await patient.respond(message['text'])

            # Send response back
            await websocket.send_json({
                "response": response,
                "timestamp": message.get('timestamp')
            })

    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()

@router.delete("/{session_id}")
async def end_patient_session(session_id: str):
    """End AI patient session"""
    if session_id in active_patients:
        del active_patients[session_id]
        return {"message": "Session ended"}
    else:
        raise HTTPException(status_code=404, detail="Session not found")
```

**Validation:**
- [ ] AI patient stays in character (no "As an AI..." responses)
- [ ] Emotional states reflect in responses (tearful patient pauses, anxious patient interrupts)
- [ ] Information disclosed progressively (not all at once)
- [ ] Responds positively to empathy
- [ ] Conversation flows naturally
- [ ] Australian medical terminology used

**Time Estimate:** 40 hours

---

### Task 2: AI Examiner Scoring (30 hours)

**Priority:** P0 (CRITICAL - exam realism depends on accurate scoring)

**AI Examiner Agent:**

```python
# backend/agents/ai_examiner_agent.py
from langchain.chat_models import ChatAnthropic
from langchain.schema import SystemMessage, HumanMessage
from typing import Dict, List
import os
import json

class AIExaminerAgent:
    """
    AI Examiner Agent for real-time OSCE scoring using 15-mark rubrics.

    Features:
    - Analyzes conversation transcript in real-time
    - Assigns marks based on rubric criteria
    - Provides detailed feedback (strengths/weaknesses)
    - Determines pass/fail (9/15 threshold)
    """

    def __init__(self, rubric: Dict):
        self.rubric = rubric
        self.total_marks = rubric.get('total_marks', 15)
        self.pass_mark = rubric.get('pass_mark', 9)
        self.criteria = rubric.get('criteria', [])

        # Initialize Claude 3.5 Sonnet
        self.llm = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            temperature=0.1,  # Low temperature for consistent scoring
            max_tokens=2000,
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
        )

    async def score_conversation(self, conversation_history: List[Dict[str, str]], patient_script: Dict) -> Dict:
        """
        Score student's performance based on conversation.

        Args:
            conversation_history: Full conversation between student and patient
            patient_script: Patient scenario details

        Returns:
            Scoring result with marks, feedback, and pass/fail
        """
        system_prompt = self._build_scoring_prompt(patient_script)

        # Format conversation for analysis
        conversation_text = "\n\n".join([
            f"{turn['role'].upper()}: {turn['content']}"
            for turn in conversation_history
        ])

        user_prompt = f"""Analyze the following OSCE conversation and provide detailed scoring.

CONVERSATION:
{conversation_text}

Provide your scoring in this exact JSON format:
{{
  "total_score": <number out of {self.total_marks}>,
  "pass_fail": "<PASS or FAIL>",
  "criteria_scores": [
    {{
      "criterion": "<name>",
      "marks_awarded": <number>,
      "marks_possible": <number>,
      "justification": "<brief explanation>"
    }}
  ],
  "strengths": ["<strength 1>", "<strength 2>", ...],
  "areas_for_improvement": ["<area 1>", "<area 2>", ...],
  "overall_feedback": "<2-3 sentences of constructive feedback>"
}}"""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

        # Get AI examiner's scoring
        response = await self.llm.ainvoke(messages)
        response_text = response.content

        # Parse JSON response
        try:
            # Extract JSON from response (handle markdown code blocks)
            if "```json" in response_text:
                json_start = response_text.index("```json") + 7
                json_end = response_text.index("```", json_start)
                json_text = response_text[json_start:json_end].strip()
            else:
                json_text = response_text

            scoring_result = json.loads(json_text)

            # Add metadata
            scoring_result['total_marks_possible'] = self.total_marks
            scoring_result['pass_mark'] = self.pass_mark
            scoring_result['passed'] = scoring_result['total_score'] >= self.pass_mark

            return scoring_result

        except Exception as e:
            # Fallback if JSON parsing fails
            return {
                "total_score": 0,
                "pass_fail": "FAIL",
                "error": f"Scoring failed: {str(e)}",
                "raw_response": response_text
            }

    def _build_scoring_prompt(self, patient_script: Dict) -> str:
        """Build system prompt for examiner scoring"""

        criteria_text = "\n".join([
            f"{i+1}. {criterion['name']} ({criterion['marks']} marks): {criterion['description']}"
            for i, criterion in enumerate(self.criteria)
        ])

        return f"""You are an experienced AMC Clinical Examination examiner. Your role is to objectively score medical students' OSCE performance using the provided rubric.

PATIENT SCENARIO:
- Presenting Complaint: {patient_script['presenting_complaint']}
- Key Information: {', '.join(patient_script['key_information'])}
- Patient Concerns: {', '.join(patient_script['concerns'])}

MARKING CRITERIA (Total: {self.total_marks} marks, Pass: {self.pass_mark} marks):
{criteria_text}

SCORING GUIDELINES:
1. Be objective and evidence-based
2. Award marks only if clear evidence in conversation
3. Consider both content (what was covered) and communication skills
4. Australian AMC standards apply:
   - Appropriate greeting and introduction
   - Empathy and rapport-building
   - Systematic history-taking
   - Appropriate questioning (open to closed funnel)
   - Patient-centered approach
   - Safety-netting and appropriate follow-up
5. Common mistakes to penalize:
   - Interrupting patient before they finish speaking
   - Closed questions only (no open-ended exploration)
   - Missing red flags or safety concerns
   - Poor empathy or communication
   - Not addressing patient's concerns
   - Inadequate summarization or explanation

Be fair but rigorous. Provide constructive feedback to help students improve."""

    async def score_in_real_time(self, conversation_history: List[Dict[str, str]]) -> Dict:
        """
        Provide interim scoring during conversation (every 2-3 minutes).

        Returns partial scoring to help students self-assess during practice.
        """
        # Similar to score_conversation but with interim feedback
        # Used for practice mode (not timed exam)
        pass
```

**Test AI Examiner:**

```python
# backend/tests/test_ai_examiner.py
import asyncio
from agents.ai_examiner_agent import AIExaminerAgent
from utils.osce_loader import OSCELoader

async def test_ai_examiner():
    # Load OSCE
    loader = OSCELoader()
    osce = loader.get_osce_by_id("respiratory_001")
    rubric = loader.get_rubric(osce)
    patient_script = loader.get_patient_script(osce)

    # Create AI examiner
    examiner = AIExaminerAgent(rubric)

    # Mock conversation (good performance)
    good_conversation = [
        {"role": "student", "content": "Hello, I'm Dr. Chen. Thank you for coming in today. How can I help you?"},
        {"role": "patient", "content": "Hi Doctor. I've had this cough for about 3 weeks now and it's not getting better."},
        {"role": "student", "content": "I see. A 3-week cough must be quite concerning. Can you tell me more about it?"},
        {"role": "patient", "content": "Well, it's mostly dry, but sometimes I bring up a bit of clear phlegm. It's worse at night."},
        {"role": "student", "content": "That sounds uncomfortable, especially if it's disturbing your sleep. Have you had any other symptoms like fever, shortness of breath, or chest pain?"},
        {"role": "patient", "content": "No fever, but I do get a bit short of breath when I walk up stairs. No chest pain though."},
        {"role": "student", "content": "Thank you for sharing that. I'd like to ask a few more questions to better understand what might be causing this. Have you had any recent travel, or been around anyone who's been sick?"},
        # ... (full conversation continues)
    ]

    # Score conversation
    print("\n" + "="*60)
    print("AI EXAMINER SCORING TEST")
    print("="*60)

    result = await examiner.score_conversation(good_conversation, patient_script)

    print(f"\nTotal Score: {result['total_score']}/{result['total_marks_possible']}")
    print(f"Pass/Fail: {result['pass_fail']} (Pass mark: {result['pass_mark']})")
    print(f"\nCriteria Scores:")
    for criterion in result['criteria_scores']:
        print(f"  - {criterion['criterion']}: {criterion['marks_awarded']}/{criterion['marks_possible']}")
        print(f"    Justification: {criterion['justification']}")

    print(f"\nStrengths:")
    for strength in result['strengths']:
        print(f"  ✓ {strength}")

    print(f"\nAreas for Improvement:")
    for area in result['areas_for_improvement']:
        print(f"  • {area}")

    print(f"\nOverall Feedback:")
    print(f"  {result['overall_feedback']}")

if __name__ == "__main__":
    asyncio.run(test_ai_examiner())
```

**API Endpoint for Scoring:**

```python
# backend/api/routes/ai_examiner.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from agents.ai_examiner_agent import AIExaminerAgent
from utils.osce_loader import OSCELoader

router = APIRouter(prefix="/api/ai-examiner", tags=["ai-examiner"])

class ScoreRequest(BaseModel):
    osce_id: str
    conversation_history: List[Dict[str, str]]

@router.post("/score")
async def score_osce_performance(request: ScoreRequest):
    """Score student's OSCE performance"""
    try:
        # Load OSCE
        loader = OSCELoader()
        osce = loader.get_osce_by_id(request.osce_id)
        rubric = loader.get_rubric(osce)
        patient_script = loader.get_patient_script(osce)

        # Create AI examiner
        examiner = AIExaminerAgent(rubric)

        # Score conversation
        result = await examiner.score_conversation(
            request.conversation_history,
            patient_script
        )

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**Validation:**
- [ ] Scoring is consistent (same conversation = similar score)
- [ ] Marks align with rubric criteria
- [ ] Feedback is constructive and specific
- [ ] Pass/fail threshold correct (9/15 marks)
- [ ] Edge cases handled (very short conversation, student did nothing)

**Time Estimate:** 30 hours

---

### Task 3: WebRTC Frontend (40 hours)

**Priority:** P0 (CRITICAL - user interface)

**Setup Frontend:**

```bash
cd /home/dev/Development/irStudy/amc-simulation
mkdir -p frontend
cd frontend

npm create vite@latest . -- --template react-ts
npm install
npm install \
  react-router-dom \
  @tanstack/react-query \
  zustand \
  tailwindcss postcss autoprefixer \
  simple-peer \
  socket.io-client \
  wavesurfer.js \
  react-use-websocket \
  date-fns \
  lucide-react

npx tailwindcss init -p
```

**WebRTC Hook:**

```typescript
// src/hooks/useWebRTC.ts
import { useEffect, useRef, useState } from 'react';
import SimplePeer from 'simple-peer';

interface UseWebRTCOptions {
  audio?: boolean;
  video?: boolean;
  onStream?: (stream: MediaStream) => void;
  onData?: (data: any) => void;
}

export const useWebRTC = (options: UseWebRTCOptions = {}) => {
  const [localStream, setLocalStream] = useState<MediaStream | null>(null);
  const [remoteStream, setRemoteStream] = useState<MediaStream | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const peerRef = useRef<SimplePeer.Instance | null>(null);
  const localVideoRef = useRef<HTMLVideoElement>(null);
  const remoteVideoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    // Get user media (microphone + camera)
    const getUserMedia = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          audio: options.audio ?? true,
          video: options.video ?? false // AMC exam is audio-only (for now)
        });

        setLocalStream(stream);

        if (localVideoRef.current) {
          localVideoRef.current.srcObject = stream;
        }

        if (options.onStream) {
          options.onStream(stream);
        }
      } catch (err) {
        setError('Failed to access microphone/camera');
        console.error('getUserMedia error:', err);
      }
    };

    getUserMedia();

    return () => {
      // Cleanup: stop all tracks
      if (localStream) {
        localStream.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  const initializePeer = (initiator: boolean, signalData?: SimplePeer.SignalData) => {
    if (!localStream) {
      setError('Local stream not available');
      return;
    }

    const peer = new SimplePeer({
      initiator,
      trickle: false,
      stream: localStream,
    });

    peer.on('signal', (data) => {
      // Send signal data to server for peer connection
      console.log('Signal data:', data);
      // In production, send via WebSocket to signaling server
    });

    peer.on('stream', (stream) => {
      setRemoteStream(stream);

      if (remoteVideoRef.current) {
        remoteVideoRef.current.srcObject = stream;
      }
    });

    peer.on('connect', () => {
      setIsConnected(true);
    });

    peer.on('data', (data) => {
      const message = JSON.parse(data.toString());
      if (options.onData) {
        options.onData(message);
      }
    });

    peer.on('error', (err) => {
      setError(err.message);
      console.error('Peer error:', err);
    });

    if (signalData) {
      peer.signal(signalData);
    }

    peerRef.current = peer;
  };

  const sendData = (data: any) => {
    if (peerRef.current && isConnected) {
      peerRef.current.send(JSON.stringify(data));
    }
  };

  const stopStream = () => {
    if (localStream) {
      localStream.getTracks().forEach(track => track.stop());
      setLocalStream(null);
    }

    if (peerRef.current) {
      peerRef.current.destroy();
      peerRef.current = null;
    }

    setIsConnected(false);
  };

  return {
    localStream,
    remoteStream,
    isConnected,
    error,
    localVideoRef,
    remoteVideoRef,
    initializePeer,
    sendData,
    stopStream
  };
};
```

**OSCE Station Component:**

```typescript
// src/pages/OSCEStation.tsx
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Mic, MicOff, Video, VideoOff, Timer, AlertCircle } from 'lucide-react';
import { useWebRTC } from '../hooks/useWebRTC';
import { useWebSocket } from 'react-use-websocket';
import PatientVideo from '../components/PatientVideo';
import ConversationTranscript from '../components/ConversationTranscript';
import RubricDisplay from '../components/RubricDisplay';

const OSCEStation: React.FC = () => {
  const { osceId } = useParams<{ osceId: string }>();
  const navigate = useNavigate();

  const [sessionId, setSessionId] = useState<string | null>(null);
  const [patientInfo, setPatientInfo] = useState<any>(null);
  const [conversation, setConversation] = useState<any[]>([]);
  const [timeRemaining, setTimeRemaining] = useState(8 * 60); // 8 minutes
  const [isTimedMode, setIsTimedMode] = useState(false);
  const [audioEnabled, setAudioEnabled] = useState(true);

  // WebSocket connection to AI patient
  const WS_URL = `ws://localhost:8001/api/ai-patient/ws/${sessionId}`;
  const { sendMessage, lastMessage } = useWebSocket(
    sessionId ? WS_URL : null,
    {
      shouldReconnect: () => true,
    }
  );

  // Initialize OSCE session
  useEffect(() => {
    const initSession = async () => {
      try {
        const response = await fetch('http://localhost:8001/api/ai-patient/start', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            osce_id: osceId,
            emotional_state: 'anxious'
          })
        });

        const data = await response.json();
        setSessionId(data.session_id);
        setPatientInfo(data);
      } catch (err) {
        console.error('Failed to start session:', err);
      }
    };

    initSession();
  }, [osceId]);

  // Handle incoming messages from AI patient
  useEffect(() => {
    if (lastMessage) {
      const message = JSON.parse(lastMessage.data);
      setConversation(prev => [
        ...prev,
        { role: 'patient', content: message.response, timestamp: new Date() }
      ]);
    }
  }, [lastMessage]);

  // Timer countdown (timed mode)
  useEffect(() => {
    if (!isTimedMode) return;

    const interval = setInterval(() => {
      setTimeRemaining(prev => {
        if (prev <= 1) {
          clearInterval(interval);
          handleEndStation();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(interval);
  }, [isTimedMode]);

  const handleStudentMessage = (message: string) => {
    // Add to conversation
    setConversation(prev => [
      ...prev,
      { role: 'student', content: message, timestamp: new Date() }
    ]);

    // Send to AI patient via WebSocket
    sendMessage(JSON.stringify({ text: message, timestamp: Date.now() }));
  };

  const handleEndStation = async () => {
    // Get final scoring
    try {
      const response = await fetch('http://localhost:8001/api/ai-examiner/score', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          osce_id: osceId,
          conversation_history: conversation
        })
      });

      const scoringResult = await response.json();
      navigate(`/results/${sessionId}`, { state: { scoringResult } });
    } catch (err) {
      console.error('Scoring failed:', err);
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Left Panel - Patient Video + Info */}
      <div className="w-2/3 p-4 space-y-4">
        {/* Timer */}
        {isTimedMode && (
          <div className={`card ${timeRemaining < 60 ? 'bg-red-50 border-red-500' : ''}`}>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Timer className={timeRemaining < 60 ? 'text-red-600' : 'text-primary-600'} size={24} />
                <span className="font-medium">Time Remaining</span>
              </div>
              <div className={`text-3xl font-bold ${timeRemaining < 60 ? 'text-red-600' : 'text-primary-600'}`}>
                {formatTime(timeRemaining)}
              </div>
            </div>
          </div>
        )}

        {/* Patient Info */}
        <div className="card">
          <h2 className="font-semibold mb-2">Patient Information</h2>
          <div className="text-sm text-gray-600">
            <p><strong>Name:</strong> {patientInfo?.patient_name}</p>
            <p><strong>Presenting Complaint:</strong> {patientInfo?.presenting_complaint}</p>
          </div>
        </div>

        {/* Patient Video/Avatar */}
        <PatientVideo emotional_state={patientInfo?.emotional_state} />

        {/* Conversation Transcript */}
        <ConversationTranscript
          conversation={conversation}
          onSendMessage={handleStudentMessage}
          audioEnabled={audioEnabled}
        />
      </div>

      {/* Right Panel - Rubric + Controls */}
      <div className="w-1/3 p-4 bg-white border-l border-gray-200 space-y-4">
        <RubricDisplay osceId={osceId!} />

        {/* Controls */}
        <div className="space-y-2">
          <button
            onClick={() => setAudioEnabled(!audioEnabled)}
            className={`w-full flex items-center justify-center gap-2 px-4 py-2 rounded-lg ${
              audioEnabled ? 'bg-green-600 text-white' : 'bg-gray-300 text-gray-700'
            }`}
          >
            {audioEnabled ? <Mic size={20} /> : <MicOff size={20} />}
            {audioEnabled ? 'Microphone On' : 'Microphone Off'}
          </button>

          <button
            onClick={handleEndStation}
            className="w-full btn-primary"
          >
            End Station & Get Feedback
          </button>
        </div>
      </div>
    </div>
  );
};

export default OSCEStation;
```

**Validation:**
- [ ] WebRTC audio works (microphone access granted)
- [ ] WebSocket connection stable
- [ ] Messages sent/received in real-time
- [ ] Timer countdown accurate
- [ ] End station triggers scoring
- [ ] Mobile-responsive (or desktop warning)

**Time Estimate:** 40 hours

---

### Task 4: Text-to-Speech (ElevenLabs) (15 hours)

```python
# backend/services/elevenlabs_service.py
from elevenlabs import generate, Voice, VoiceSettings
import os

class ElevenLabsService:
    """Text-to-speech using ElevenLabs with emotional voices"""

    def __init__(self):
        self.api_key = os.getenv("ELEVENLABS_API_KEY")
        # Voice IDs for different emotional states
        self.voices = {
            'neutral': 'EXAVITQu4vr4xnSDxMaL',  # Sarah (Australian female)
            'anxious': 'ErXwobaYiN019PkySvjV',  # Emma (anxious tone)
            'tearful': 'MF3mGyEYCl7XYWbV9V6O',  # Nicole (emotional)
        }

    async def synthesize_speech(
        self,
        text: str,
        emotional_state: str = 'neutral',
        output_path: str = None
    ) -> bytes:
        """
        Convert text to speech with emotional voice.

        Args:
            text: Patient's response text
            emotional_state: 'neutral', 'anxious', 'tearful', etc.
            output_path: Optional path to save audio file

        Returns:
            Audio bytes (MP3 format)
        """
        voice_id = self.voices.get(emotional_state, self.voices['neutral'])

        audio = generate(
            text=text,
            voice=Voice(
                voice_id=voice_id,
                settings=VoiceSettings(
                    stability=0.5,
                    similarity_boost=0.75,
                    style=0.5 if emotional_state != 'neutral' else 0.0
                )
            ),
            api_key=self.api_key
        )

        if output_path:
            with open(output_path, 'wb') as f:
                f.write(audio)

        return audio
```

### Task 5: Speech-to-Text (Whisper) (15 hours)

```python
# backend/services/whisper_service.py
from openai import OpenAI
import os

class WhisperService:
    """Speech-to-text using OpenAI Whisper"""

    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    async def transcribe(self, audio_file_path: str) -> str:
        """
        Transcribe audio to text.

        Args:
            audio_file_path: Path to audio file (MP3, WAV, etc.)

        Returns:
            Transcribed text
        """
        with open(audio_file_path, 'rb') as audio_file:
            transcription = self.client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="en"  # Australian English
            )

        return transcription.text
```

### Task 6: Real-time Scoring UI (20 hours)

```typescript
// src/components/RubricDisplay.tsx
// Live rubric with marks allocated as conversation progresses
```

### Task 7: Testing (30 hours)

**AI Patient Quality Test:**

```python
# Test 50 random OSCEs to ensure AI patient quality
# Metrics: stays in character, discloses information appropriately, responds to empathy
```

**Scoring Accuracy Test:**

```python
# Compare AI examiner scores vs. human expert scores
# Target: ±2 marks difference
```

**Validation:**
- [ ] AI patient realism: 90%+ user satisfaction
- [ ] Scoring accuracy: ±2 marks vs. human
- [ ] Voice synthesis sounds natural
- [ ] Speech recognition 95%+ accuracy
- [ ] WebRTC stable for 8-minute sessions

**Time Estimate:** 30 hours

---

## 📊 Success Metrics

### Completion Criteria
- [ ] AI patient conversational and realistic
- [ ] AI examiner scoring ±2 marks accurate
- [ ] WebRTC audio functional
- [ ] Voice synthesis natural (ElevenLabs)
- [ ] Speech transcription accurate (Whisper)
- [ ] Real-time scoring UI displays rubric
- [ ] 50+ OSCEs tested successfully

### Quality Gates
- [ ] AI patient Turing test: 70%+ realism
- [ ] Scoring accuracy: ±2 marks
- [ ] Voice quality: 4.5/5 stars
- [ ] WebRTC reliability: 99%+ uptime
- [ ] End-to-end latency: < 3 seconds

---

## 🔗 Related Documents

- **[README.md](./README.md)** - Overall plan
- **[01_PHASE1_MOBILE_QUICK_SEARCH.md](./01_PHASE1_MOBILE_QUICK_SEARCH.md)** - Phase 1
- **[02_PHASE2_EMR_PRACTICE.md](./02_PHASE2_EMR_PRACTICE.md)** - Phase 2

---

**Last Updated:** 2026-02-01
**Owner:** AI/ML Engineer + Full-Stack Developer
**Estimated Completion:** 2026-04-26 (6 weeks after Phase 2)
