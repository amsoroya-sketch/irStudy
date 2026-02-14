#!/usr/bin/env python3
"""
AMC Clinical Exam Simulation - Architecture Diagram Generator

This script generates comprehensive architecture diagrams for the AMC Clinical
Examination Simulation system using the Python 'diagrams' library.

Generates 12 detailed diagrams covering:
- System architecture (4-layer design)
- Data flow and message routing
- Agent architecture (6 SIM-* agents)
- State machines (session and emotional states)
- Database schema
- WebSocket protocol
- Deployment architecture
- Integration with existing systems

Requirements:
    - diagrams==0.25.1
    - graphviz==0.20.3

Usage:
    python3 generate_amc_simulation_diagrams.py
"""

from pathlib import Path
from diagrams import Diagram, Cluster, Edge, Node
from diagrams.custom import Custom
from diagrams.programming.framework import FastAPI, React
from diagrams.programming.language import Python, TypeScript
from diagrams.onprem.database import PostgreSQL
from diagrams.onprem.inmemory import Redis
from diagrams.onprem.network import Nginx
from diagrams.onprem.container import Docker
from diagrams.generic.blank import Blank
from diagrams.generic.database import SQL
from diagrams.generic.device import Mobile, Tablet
from diagrams.generic.network import Router, Firewall
from diagrams.generic.os import Ubuntu, LinuxGeneral
from diagrams.generic.storage import Storage


# Output directory for diagrams
OUTPUT_DIR = Path(__file__).parent / "images"
OUTPUT_DIR.mkdir(exist_ok=True)

# Common graph attributes for consistent styling
GRAPH_ATTR = {
    "fontsize": "14",
    "bgcolor": "white",
    "pad": "0.5",
    "nodesep": "0.8",
    "ranksep": "1.0"
}

NODE_ATTR = {
    "fontsize": "12",
}

EDGE_ATTR = {
    "fontsize": "10",
}


def diagram_01_system_architecture_4layer():
    """
    Diagram 01: System Architecture - Four-Layer Design

    Shows the high-level architecture with four distinct layers:
    1. Presentation Layer (Frontend)
    2. Orchestration Layer (Backend API)
    3. Intelligence Layer (AI Agents)
    4. Data Layer (Storage)
    """
    print("Generating Diagram 01: System Architecture (4-Layer)...")

    with Diagram(
        "AMC Simulation - System Architecture (4-Layer Design)",
        filename=str(OUTPUT_DIR / "01_system_architecture_4layer"),
        outformat="png",
        show=False,
        direction="TB",
        graph_attr=GRAPH_ATTR,
        node_attr=NODE_ATTR,
        edge_attr=EDGE_ATTR
    ):
        # Layer 1: Presentation
        with Cluster("Layer 1: Presentation (Frontend)"):
            react_ui = React("React UI\nOSCE Station")
            websocket_client = Python("WebSocket Client\nReal-time Comms")
            webrtc = Python("WebRTC\nAudio/Video")

            react_ui >> Edge(label="manages") >> websocket_client
            react_ui >> Edge(label="uses") >> webrtc

        # Layer 2: Orchestration
        with Cluster("Layer 2: Orchestration (Backend API)"):
            fastapi = FastAPI("FastAPI\nREST + WebSocket")
            orchestrator = Python("SIM-003\nOrchestrator")
            context_mgr = Python("SIM-004\nContext Manager")

            fastapi >> Edge(label="routes") >> orchestrator
            orchestrator >> Edge(label="uses") >> context_mgr

        # Layer 3: Intelligence
        with Cluster("Layer 3: Intelligence (AI Agents)"):
            ai_patient = Python("SIM-001\nAI Patient")
            ai_examiner = Python("SIM-002\nAI Examiner")
            claude = Python("Claude 3.5\nSonnet API")
            qa_agents = Python("QA-001/002\nValidators")

            ai_patient >> Edge(label="calls") >> claude
            ai_examiner >> Edge(label="calls") >> claude
            ai_patient >> Edge(label="validated by") >> qa_agents
            ai_examiner >> Edge(label="validated by") >> qa_agents

        # Layer 4: Data
        with Cluster("Layer 4: Data (Storage)"):
            redis = Redis("Redis\nSession State")
            postgres = PostgreSQL("PostgreSQL\nPersistent Data")

            redis - Edge(label="final save") - postgres

        # Connections between layers
        websocket_client >> Edge(label="WebSocket", color="blue") >> fastapi
        fastapi >> Edge(label="invokes") >> orchestrator
        orchestrator >> Edge(label="delegates") >> ai_patient
        orchestrator >> Edge(label="delegates") >> ai_examiner

        context_mgr >> Edge(label="reads/writes") >> redis
        orchestrator >> Edge(label="saves session") >> postgres
        ai_patient >> Edge(label="stores history") >> redis

    print("✓ Diagram 01 generated")


def diagram_02_data_flow_osce_session():
    """
    Diagram 02: Data Flow - Complete OSCE Session

    Shows the end-to-end data flow from candidate start to feedback:
    - User interaction
    - Message routing
    - AI processing
    - Scoring
    - Results delivery
    """
    print("Generating Diagram 02: Data Flow - OSCE Session...")

    with Diagram(
        "AMC Simulation - Data Flow (Complete OSCE Session)",
        filename=str(OUTPUT_DIR / "02_data_flow_osce_session"),
        outformat="png",
        show=False,
        direction="LR",
        graph_attr=GRAPH_ATTR,
        node_attr=NODE_ATTR,
        edge_attr=EDGE_ATTR
    ):
        # Components
        user = Mobile("Candidate\n(Medical Student)")
        frontend = React("React UI")
        ws_conn = Python("WebSocket\nConnection")
        orchestrator = Python("SIM-003\nOrchestrator")
        context = Python("SIM-004\nContext")
        ai_patient = Python("SIM-001\nAI Patient")
        ai_examiner = Python("SIM-002\nExaminer")
        redis = Redis("Redis\nSession")
        postgres = PostgreSQL("PostgreSQL\nFinal Data")
        results = React("Results\nPage")

        # Data flow
        user >> Edge(label="1. Start OSCE", color="blue") >> frontend
        frontend >> Edge(label="2. Connect WS", color="blue") >> ws_conn
        ws_conn >> Edge(label="3. Init session", color="blue") >> orchestrator
        orchestrator >> Edge(label="4. Load patient", color="green") >> ai_patient
        ai_patient >> Edge(label="5. Opening statement", color="green") >> orchestrator
        orchestrator >> Edge(label="6. Send to UI", color="green") >> ws_conn
        ws_conn >> Edge(label="7. Display", color="green") >> frontend
        frontend >> Edge(label="8. Candidate asks", color="purple") >> ws_conn
        ws_conn >> Edge(label="9. Message", color="purple") >> orchestrator
        orchestrator >> Edge(label="10. Store msg", color="purple") >> context
        context >> Edge(label="11. Save", color="purple") >> redis
        orchestrator >> Edge(label="12. Get response", color="orange") >> ai_patient
        ai_patient >> Edge(label="13. Reply", color="orange") >> orchestrator
        orchestrator >> Edge(label="14. Send", color="orange") >> ws_conn
        ws_conn >> Edge(label="15. Display", color="orange") >> frontend
        frontend >> Edge(label="16. End station", color="red") >> ws_conn
        ws_conn >> Edge(label="17. Finalize", color="red") >> orchestrator
        orchestrator >> Edge(label="18. Score", color="red") >> ai_examiner
        ai_examiner >> Edge(label="19. Feedback", color="red") >> orchestrator
        orchestrator >> Edge(label="20. Save final", color="red") >> postgres
        orchestrator >> Edge(label="21. Results", color="red") >> results
        results >> Edge(label="22. View", color="red") >> user

    print("✓ Diagram 02 generated")


def diagram_03_agent_architecture_overview():
    """
    Diagram 03: Agent Architecture Overview

    Shows all agents in the system:
    - Base classes (BaseAgent, BaseMedicalExpert)
    - 6 new SIM-* agents
    - Integration with existing QA agents
    - Medical expert agents (MED-001, MED-002)
    """
    print("Generating Diagram 03: Agent Architecture Overview...")

    with Diagram(
        "AMC Simulation - Agent Architecture Overview",
        filename=str(OUTPUT_DIR / "03_agent_architecture_overview"),
        outformat="png",
        show=False,
        direction="TB",
        graph_attr=GRAPH_ATTR,
        node_attr=NODE_ATTR,
        edge_attr=EDGE_ATTR
    ):
        # Base classes
        with Cluster("Base Classes"):
            base_agent = Python("BaseAgent\n(Abstract)")
            base_medical = Python("BaseMedicalExpert\n(Inherits BaseAgent)")

            base_agent >> Edge(label="inherits") >> base_medical

        # New simulation agents
        with Cluster("NEW: Simulation Agents (SIM-*)"):
            sim001 = Python("SIM-001\nAI Patient\nConversational")
            sim002 = Python("SIM-002\nAI Examiner\nScoring")
            sim003 = Python("SIM-003\nOrchestrator\nSession Mgmt")
            sim004 = Python("SIM-004\nContext Manager\nHistory")
            sim005 = Python("SIM-005\nPhysical Exam\n(Future)")
            sim006 = Python("SIM-006\nAnalytics\nPerformance")

        # Existing agents
        with Cluster("Existing: Quality Assurance"):
            qa001 = Python("QA-001\nAustralian\nCompliance")
            qa002 = Python("QA-002\nClinical\nAccuracy")

        with Cluster("Existing: Medical Experts"):
            med001 = Python("MED-001\nCardiology")
            med002 = Python("MED-002\nRespiratory")

        # Inheritance
        base_medical >> Edge(label="inherits") >> sim001
        base_agent >> Edge(label="inherits") >> sim002
        base_agent >> Edge(label="inherits") >> sim003
        base_agent >> Edge(label="inherits") >> sim004
        base_agent >> Edge(label="inherits") >> sim006

        # Integration
        sim001 >> Edge(label="validated by", style="dashed") >> qa001
        sim001 >> Edge(label="validated by", style="dashed") >> qa002
        sim002 >> Edge(label="validated by", style="dashed") >> qa002

        sim003 >> Edge(label="coordinates", color="blue") >> sim001
        sim003 >> Edge(label="coordinates", color="blue") >> sim002
        sim003 >> Edge(label="uses", color="blue") >> sim004

        # Content generation
        med001 >> Edge(label="generates\npersonas", style="dotted") >> sim001
        med002 >> Edge(label="generates\npersonas", style="dotted") >> sim001

    print("✓ Diagram 03 generated")


def diagram_04_sim001_ai_patient_detail():
    """
    Diagram 04: SIM-001 AI Patient Agent - Detailed Design

    Shows the internal architecture of the AI Patient agent:
    - Class structure
    - Key attributes
    - Methods
    - Dependencies
    """
    print("Generating Diagram 04: SIM-001 AI Patient Detail...")

    with Diagram(
        "SIM-001: AI Patient Agent - Detailed Architecture",
        filename=str(OUTPUT_DIR / "04_sim001_ai_patient_detail"),
        outformat="png",
        show=False,
        direction="TB",
        graph_attr=GRAPH_ATTR,
        node_attr=NODE_ATTR,
        edge_attr=EDGE_ATTR
    ):
        with Cluster("SIM-001: AIPatientAgent"):
            # Attributes
            with Cluster("Attributes"):
                patient_script = Storage("patient_script: Dict")
                emotional_state = Storage("emotional_state: str")
                memory = Storage("memory:\nConversationBufferMemory")
                llm = Python("llm:\nChatAnthropic\n(temp=0.7)")

            # Methods
            with Cluster("Methods"):
                respond = Python("async respond()\nGenerate response")
                update_emotion = Python("update_emotional_state()\nChange emotion")
                get_history = Python("get_conversation_history()\nRetrieve history")
                reset = Python("reset()\nClear memory")
                build_prompt = Python("_build_system_prompt()\nConstruct persona")

        # Dependencies
        with Cluster("Dependencies"):
            claude_api = Python("Claude 3.5 Sonnet\nAnthropic API")
            langchain = Python("LangChain\nConversation Memory")
            qa001 = Python("QA-001\nAustralian Compliance")

        # External data
        with Cluster("Data Sources"):
            osce_loader = Python("OSCELoader\nLoad patient script")
            persona_db = SQL("Patient Personas\n200+ profiles")

        # Flow
        osce_loader >> Edge(label="loads") >> patient_script
        persona_db >> Edge(label="maps to") >> patient_script
        patient_script >> Edge(label="uses") >> build_prompt
        build_prompt >> Edge(label="creates prompt") >> respond
        respond >> Edge(label="calls") >> llm
        llm >> Edge(label="API request") >> claude_api
        respond >> Edge(label="stores") >> memory
        respond >> Edge(label="validated by") >> qa001
        emotional_state >> Edge(label="affects") >> build_prompt
        update_emotion >> Edge(label="modifies") >> emotional_state
        memory >> Edge(label="retrieved by") >> get_history
        reset >> Edge(label="clears") >> memory

    print("✓ Diagram 04 generated")


def diagram_05_sim002_examiner_detail():
    """
    Diagram 05: SIM-002 AI Examiner Agent - Detailed Design

    Shows the internal architecture of the AI Examiner agent:
    - Rubric-based scoring
    - Feedback generation
    - AMC 15-mark system
    """
    print("Generating Diagram 05: SIM-002 AI Examiner Detail...")

    with Diagram(
        "SIM-002: AI Examiner Agent - Detailed Architecture",
        filename=str(OUTPUT_DIR / "05_sim002_examiner_detail"),
        outformat="png",
        show=False,
        direction="TB",
        graph_attr=GRAPH_ATTR,
        node_attr=NODE_ATTR,
        edge_attr=EDGE_ATTR
    ):
        with Cluster("SIM-002: AIExaminerAgent"):
            # Attributes
            with Cluster("Attributes"):
                rubric = Storage("rubric: Dict\n15-mark system")
                total_marks = Storage("total_marks: 15")
                pass_mark = Storage("pass_mark: 9")
                criteria = Storage("criteria: List[Dict]\n5 categories")
                llm = Python("llm:\nChatAnthropic\n(temp=0.1)")

            # Methods
            with Cluster("Methods"):
                score_conv = Python("async score_conversation()\nFinal scoring")
                score_realtime = Python("async score_in_real_time()\nInterim scoring")
                build_scoring = Python("_build_scoring_prompt()\nRubric prompt")
                parse_json = Python("_parse_scoring_result()\nExtract JSON")

        # Dependencies
        with Cluster("Dependencies"):
            claude_api = Python("Claude 3.5 Sonnet\nAnthropic API")
            qa002 = Python("QA-002\nClinical Accuracy")

        # External data
        with Cluster("Data Sources"):
            rubric_db = SQL("AMC Rubrics\n20+ rubrics")
            conversation = Storage("Conversation History\nFrom SIM-004")
            patient_script = Storage("Patient Script\nContext")

        # Flow
        rubric_db >> Edge(label="loads") >> rubric
        conversation >> Edge(label="input") >> score_conv
        patient_script >> Edge(label="context") >> build_scoring
        rubric >> Edge(label="criteria") >> build_scoring
        build_scoring >> Edge(label="system prompt") >> score_conv
        score_conv >> Edge(label="API call") >> llm
        llm >> Edge(label="request") >> claude_api
        score_conv >> Edge(label="raw output") >> parse_json
        parse_json >> Edge(label="scoring result") >> Storage("JSON Output\nMarks+Feedback")
        score_conv >> Edge(label="validated by") >> qa002
        score_realtime >> Edge(label="periodic") >> score_conv

    print("✓ Diagram 05 generated")


def diagram_06_sim003_orchestrator_detail():
    """
    Diagram 06: SIM-003 OSCE Session Orchestrator - Detailed Design

    Shows the orchestrator that manages the entire OSCE session:
    - WebSocket management
    - State machine
    - Message routing
    - Timer management
    """
    print("Generating Diagram 06: SIM-003 Orchestrator Detail...")

    with Diagram(
        "SIM-003: OSCE Session Orchestrator - Detailed Architecture",
        filename=str(OUTPUT_DIR / "06_sim003_orchestrator_detail"),
        outformat="png",
        show=False,
        direction="LR",
        graph_attr=GRAPH_ATTR,
        node_attr=NODE_ATTR,
        edge_attr=EDGE_ATTR
    ):
        with Cluster("SIM-003: OSCESessionOrchestrator"):
            # Attributes
            with Cluster("State Management"):
                active_sessions = Storage("active_sessions:\nDict[str, SessionState]")
                timer_tasks = Storage("timer_tasks:\nDict[str, Task]")

            # Core methods
            with Cluster("Core Methods"):
                initialize = Python("async initialize_session()\nSetup OSCE")
                handle_ws = Python("async handle_websocket()\nWS connection")
                route_msg = Python("async route_message()\nMessage routing")
                manage_timer = Python("async manage_timer()\n8-min countdown")
                finalize = Python("async finalize_session()\nEnd & score")

            # Supporting methods
            with Cluster("Supporting Methods"):
                pause = Python("async pause_session()")
                resume = Python("async resume_session()")
                emergency = Python("async emergency_stop()")

        # Components it coordinates
        with Cluster("Managed Components"):
            sim001 = Python("SIM-001\nAI Patient")
            sim002 = Python("SIM-002\nExaminer")
            sim004 = Python("SIM-004\nContext")

        # Infrastructure
        with Cluster("Infrastructure"):
            websocket = Router("WebSocket\nConnections")
            redis = Redis("Redis\nSession State")
            postgres = PostgreSQL("PostgreSQL\nFinal Data")

        # Flow
        initialize >> Edge(label="creates") >> sim001
        initialize >> Edge(label="creates") >> sim002
        initialize >> Edge(label="creates") >> sim004
        initialize >> Edge(label="stores") >> active_sessions
        initialize >> Edge(label="starts") >> manage_timer

        handle_ws >> Edge(label="accepts") >> websocket
        handle_ws >> Edge(label="receives") >> route_msg

        route_msg >> Edge(label="candidate msg") >> sim004
        route_msg >> Edge(label="get response") >> sim001
        route_msg >> Edge(label="send back") >> websocket

        manage_timer >> Edge(label="countdown") >> Storage("Time\nRemaining")
        manage_timer >> Edge(label="at 0s") >> finalize

        finalize >> Edge(label="score") >> sim002
        finalize >> Edge(label="save") >> postgres
        finalize >> Edge(label="cleanup") >> redis

        active_sessions >> Edge(label="persist") >> redis
        pause >> Edge(label="pauses") >> manage_timer
        resume >> Edge(label="resumes") >> manage_timer

    print("✓ Diagram 06 generated")


def diagram_07_state_machine_session():
    """
    Diagram 07: OSCE Session State Machine

    Shows the lifecycle states of an OSCE session:
    - setup → active → warning → complete
    - Transition triggers
    """
    print("Generating Diagram 07: Session State Machine...")

    with Diagram(
        "OSCE Session State Machine",
        filename=str(OUTPUT_DIR / "07_state_machine_session"),
        outformat="png",
        show=False,
        direction="LR",
        graph_attr=GRAPH_ATTR,
        node_attr=NODE_ATTR,
        edge_attr=EDGE_ATTR
    ):
        # States (using Blank for circles)
        init = Blank("● START")
        setup = Python("SETUP\nLoad OSCE\nCreate agents")
        active = Python("ACTIVE\nConversation\n0-7 minutes")
        warning = Python("WARNING\n1 minute left\n7-8 minutes")
        complete = Python("COMPLETE\nScoring\nFeedback")
        end = Blank("● END")

        # Paused state (optional)
        paused = Python("PAUSED\nTechnical issue")

        # Transitions
        init >> Edge(label="User starts OSCE", color="blue") >> setup
        setup >> Edge(label="Session initialized\nTimer starts", color="green") >> active
        active >> Edge(label="Timer reaches 7:00", color="orange") >> warning
        warning >> Edge(label="Timer reaches 8:00 OR\nUser clicks End", color="red") >> complete
        complete >> Edge(label="Results displayed", color="purple") >> end

        # Pause transitions
        active >> Edge(label="User pauses\n(practice mode)", style="dashed") >> paused
        paused >> Edge(label="User resumes", style="dashed") >> active

        # Emergency stop
        active >> Edge(label="Emergency stop\n(error)", style="dotted", color="red") >> complete
        warning >> Edge(label="Emergency stop\n(error)", style="dotted", color="red") >> complete

    print("✓ Diagram 07 generated")


def diagram_08_state_machine_emotions():
    """
    Diagram 08: Patient Emotional State Machine

    Shows how patient emotions transition based on student's interactions:
    - 6 emotional states
    - Triggers for transitions
    """
    print("Generating Diagram 08: Emotional State Machine...")

    with Diagram(
        "AI Patient Emotional State Machine",
        filename=str(OUTPUT_DIR / "08_state_machine_emotions"),
        outformat="png",
        show=False,
        direction="TB",
        graph_attr=GRAPH_ATTR,
        node_attr=NODE_ATTR,
        edge_attr=EDGE_ATTR
    ):
        # Central state
        neutral = Python("NEUTRAL\nCalm,\ncooperative")

        # Other states around it
        anxious = Python("ANXIOUS\nWorried,\nquick speech")
        tearful = Python("TEARFUL\nEmotional,\npauses")
        angry = Python("ANGRY\nFrustrated,\ndefensive")
        confused = Python("CONFUSED\nUnclear,\nvague")
        defensive = Python("DEFENSIVE\nReluctant,\nguarded")

        # Transitions from neutral
        neutral >> Edge(label="Rushed questions\nNo empathy", color="orange") >> anxious
        neutral >> Edge(label="Bad news discussed\nNo support", color="blue") >> tearful
        neutral >> Edge(label="Dismissed concerns\nNot listened to", color="red") >> angry
        neutral >> Edge(label="Medical jargon\nComplex questions", color="purple") >> confused
        neutral >> Edge(label="Judgemental\nInvasive questions", color="brown") >> defensive

        # Transitions back to neutral (with empathy)
        anxious >> Edge(label="Reassurance\nEmpathy shown", color="green") >> neutral
        tearful >> Edge(label="Support given\nTime allowed", color="green") >> neutral
        angry >> Edge(label="Apology\nListening", color="green") >> neutral
        confused >> Edge(label="Clear explanation\nCheck understanding", color="green") >> neutral
        defensive >> Edge(label="Respect shown\nTrust built", color="green") >> neutral

        # Escalations
        anxious >> Edge(label="Continued pressure", style="dashed", color="red") >> tearful
        angry >> Edge(label="More dismissal", style="dashed", color="red") >> defensive
        confused >> Edge(label="More jargon", style="dashed", color="red") >> defensive

    print("✓ Diagram 08 generated")


def diagram_09_database_schema_er():
    """
    Diagram 09: Database Schema - Entity Relationship Diagram

    Shows PostgreSQL tables and Redis structures:
    - osce_sessions
    - patient_personas
    - amc_rubrics
    - users
    - Redis session state
    """
    print("Generating Diagram 09: Database Schema ER Diagram...")

    with Diagram(
        "Database Schema - Entity Relationship Diagram",
        filename=str(OUTPUT_DIR / "09_database_schema_er"),
        outformat="png",
        show=False,
        direction="TB",
        graph_attr=GRAPH_ATTR,
        node_attr=NODE_ATTR,
        edge_attr=EDGE_ATTR
    ):
        with Cluster("PostgreSQL Tables"):
            users = SQL("users\n---\nuser_id (PK)\nemail\nname\nsubscription_tier\ncreated_at")

            osces = SQL("osces\n---\nosce_id (PK)\ntitle\nspecialty\nstation_type\npersona_id (FK)\nrubric_id (FK)")

            personas = SQL("patient_personas\n---\npersona_id (PK)\nname\nage\ngender\nmedical_history\npersonality_traits")

            rubrics = SQL("amc_rubrics\n---\nrubric_id (PK)\nrubric_name\ntotal_marks\npass_mark\ncriteria (JSONB)")

            sessions = SQL("osce_sessions\n---\nsession_id (PK)\nuser_id (FK)\nosce_id (FK)\nmode\nstart_time\nend_time\nconversation (JSONB)\nscoring_result (JSONB)\nstatus")

            performance = SQL("user_performance\n---\nperformance_id (PK)\nuser_id (FK)\nsession_id (FK)\ntotal_score\npassed\ncategory_scores (JSONB)")

        with Cluster("Redis Data Structures"):
            session_state = Redis("session:{session_id}\n---\nstatus\ntime_remaining\npatient_agent_id\nconversation_turns\nwebsocket_connected")

            conversation = Redis("conversation:{session_id}\n---\nmessages[]\ninfo_disclosed[]\ncandidate_errors[]")

        # Relationships
        users >> Edge(label="1:N") >> sessions
        osces >> Edge(label="1:N") >> sessions
        personas >> Edge(label="1:N") >> osces
        rubrics >> Edge(label="1:N") >> osces
        sessions >> Edge(label="1:N") >> performance

        # Redis to PostgreSQL
        session_state >> Edge(label="final save", style="dashed") >> sessions
        conversation >> Edge(label="final save", style="dashed") >> sessions

    print("✓ Diagram 09 generated")


def diagram_10_websocket_protocol():
    """
    Diagram 10: WebSocket Protocol - Message Types

    Shows the WebSocket message protocol between client and server:
    - Message types
    - Data structures
    - Flow direction
    """
    print("Generating Diagram 10: WebSocket Protocol...")

    with Diagram(
        "WebSocket Protocol - Message Types",
        filename=str(OUTPUT_DIR / "10_websocket_protocol"),
        outformat="png",
        show=False,
        direction="LR",
        graph_attr=GRAPH_ATTR,
        node_attr=NODE_ATTR,
        edge_attr=EDGE_ATTR
    ):
        # Client and Server
        client = React("React Client\n(Browser)")
        server = FastAPI("FastAPI Server\n(WebSocket)")

        with Cluster("Client → Server Messages"):
            msg1 = Storage("candidate_message\n---\ntype: 'candidate_message'\ncontent: string\ntimestamp: number")
            msg2 = Storage("pause_session\n---\ntype: 'pause'\ntimestamp: number")
            msg3 = Storage("resume_session\n---\ntype: 'resume'\ntimestamp: number")
            msg4 = Storage("end_session\n---\ntype: 'end'\ntimestamp: number")

        with Cluster("Server → Client Messages"):
            resp1 = Storage("patient_response\n---\ntype: 'patient_response'\ncontent: string\nemotional_state: string\ntimestamp: number")
            resp2 = Storage("timer_update\n---\ntype: 'timer_update'\ntime_remaining: number\nis_warning: boolean")
            resp3 = Storage("session_complete\n---\ntype: 'session_complete'\nscoring_result: object\ntranscript: array")
            resp4 = Storage("error\n---\ntype: 'error'\nmessage: string\ncode: number")

        # Flow
        client >> Edge(label="send", color="blue") >> msg1
        msg1 >> Edge(label="") >> server

        client >> Edge(label="send", color="purple") >> msg2
        msg2 >> Edge(label="") >> server

        server >> Edge(label="") >> resp1
        resp1 >> Edge(label="receive", color="green") >> client

        server >> Edge(label="") >> resp2
        resp2 >> Edge(label="receive", color="orange") >> client

        server >> Edge(label="") >> resp3
        resp3 >> Edge(label="receive", color="red") >> client

    print("✓ Diagram 10 generated")


def diagram_11_deployment_architecture():
    """
    Diagram 11: Deployment Architecture - Docker Containers

    Shows the production deployment architecture:
    - Docker containers
    - Services
    - Networking
    - Load balancing
    """
    print("Generating Diagram 11: Deployment Architecture...")

    with Diagram(
        "Deployment Architecture - Docker & Services",
        filename=str(OUTPUT_DIR / "11_deployment_architecture"),
        outformat="png",
        show=False,
        direction="TB",
        graph_attr=GRAPH_ATTR,
        node_attr=NODE_ATTR,
        edge_attr=EDGE_ATTR
    ):
        # External access
        internet = Router("Internet")
        firewall = Firewall("Firewall\nHTTPS only")

        # Load balancer
        nginx = Nginx("Nginx\nLoad Balancer\nReverse Proxy")

        with Cluster("Docker Compose Stack"):
            # Frontend container
            with Cluster("Frontend Container"):
                react_app = React("React App\n(Production Build)")
                nginx_static = Nginx("Nginx\nStatic Server")

            # Backend containers
            with Cluster("Backend Containers (3 replicas)"):
                api1 = FastAPI("FastAPI API\nReplica 1")
                api2 = FastAPI("FastAPI API\nReplica 2")
                api3 = FastAPI("FastAPI API\nReplica 3")

            # Worker containers
            with Cluster("Worker Containers"):
                celery1 = Python("Celery Worker\nScoring Tasks")
                celery2 = Python("Celery Worker\nAnalytics Tasks")

            # Data stores
            with Cluster("Data Layer"):
                redis_main = Redis("Redis\nSession State")
                redis_queue = Redis("Redis\nCelery Queue")
                postgres_main = PostgreSQL("PostgreSQL\nMain Database")
                postgres_replica = PostgreSQL("PostgreSQL\nRead Replica")

            # Monitoring
            with Cluster("Monitoring"):
                prometheus = Python("Prometheus\nMetrics")
                grafana = Python("Grafana\nDashboards")

        # External services
        with Cluster("External APIs"):
            anthropic = Python("Anthropic API\nClaude 3.5")
            elevenlabs = Python("ElevenLabs\nVoice Synthesis")
            openai = Python("OpenAI\nWhisper STT")

        # Flow
        internet >> Edge(label="HTTPS") >> firewall
        firewall >> Edge(label="") >> nginx
        nginx >> Edge(label="static") >> nginx_static
        nginx >> Edge(label="API/WS\nround-robin") >> api1
        nginx >> Edge(label="") >> api2
        nginx >> Edge(label="") >> api3

        api1 >> Edge(label="R/W") >> redis_main
        api1 >> Edge(label="enqueue") >> redis_queue
        api1 >> Edge(label="R/W") >> postgres_main
        api1 >> Edge(label="LLM calls") >> anthropic

        celery1 >> Edge(label="dequeue") >> redis_queue
        celery1 >> Edge(label="R/W") >> postgres_main
        celery1 >> Edge(label="LLM calls") >> anthropic

        postgres_main >> Edge(label="replication") >> postgres_replica

        api1 >> Edge(label="metrics") >> prometheus
        prometheus >> Edge(label="visualize") >> grafana

    print("✓ Diagram 11 generated")


def diagram_12_integration_architecture():
    """
    Diagram 12: Integration Architecture

    Shows how AMC Simulation integrates with existing systems:
    - 46-agent medical education infrastructure
    - EMR Practice System
    - RAG (Qdrant vector database)
    - Content management
    """
    print("Generating Diagram 12: Integration Architecture...")

    with Diagram(
        "Integration Architecture - AMC Simulation + Existing Systems",
        filename=str(OUTPUT_DIR / "12_integration_architecture"),
        outformat="png",
        show=False,
        direction="TB",
        graph_attr=GRAPH_ATTR,
        node_attr=NODE_ATTR,
        edge_attr=EDGE_ATTR
    ):
        with Cluster("NEW: AMC Clinical Exam Simulation"):
            amc_frontend = React("AMC Simulation\nUI")
            sim001 = Python("SIM-001\nAI Patient")
            sim002 = Python("SIM-002\nExaminer")
            sim003 = Python("SIM-003\nOrchestrator")
            osce_db = SQL("OSCE Sessions\nDatabase")

        with Cluster("Existing: 46-Agent Infrastructure"):
            pm001 = Python("PM-001\nProject Manager")
            qa001 = Python("QA-001\nAustralian\nCompliance")
            qa002 = Python("QA-002\nClinical\nAccuracy")
            med001 = Python("MED-001\nCardiology")
            med002 = Python("MED-002\nRespiratory")

        with Cluster("Existing: EMR Practice System"):
            emr_frontend = React("EMR Practice\nUI")
            emr_api = FastAPI("EMR API")
            emr_db = SQL("EMR Sessions\nDatabase")

        with Cluster("Shared Infrastructure"):
            auth = Python("Auth Service\nJWT Tokens")
            user_db = PostgreSQL("Users\nDatabase")
            analytics = Python("Analytics\nDashboard")

        with Cluster("RAG System (Qdrant)"):
            qdrant = Storage("Qdrant\nVector DB\n9,672 chunks")
            rag_service = Python("RAG Query\nService")

        # Integration points
        amc_frontend >> Edge(label="uses") >> auth
        emr_frontend >> Edge(label="uses") >> auth
        auth >> Edge(label="validates") >> user_db

        sim001 >> Edge(label="validated by", color="orange") >> qa001
        sim001 >> Edge(label="validated by", color="orange") >> qa002
        sim002 >> Edge(label="validated by", color="orange") >> qa002

        sim001 >> Edge(label="queries for facts", style="dashed") >> rag_service
        rag_service >> Edge(label="") >> qdrant

        med001 >> Edge(label="generates personas", style="dotted") >> sim001
        med002 >> Edge(label="generates personas", style="dotted") >> sim001

        osce_db >> Edge(label="performance data") >> analytics
        emr_db >> Edge(label="performance data") >> analytics
        analytics >> Edge(label="combined dashboard") >> user_db

        pm001 >> Edge(label="coordinates", color="blue") >> sim003
        pm001 >> Edge(label="quality gates", color="blue") >> qa001

    print("✓ Diagram 12 generated")


def main():
    """
    Main function to generate all 12 diagrams
    """
    print("\n" + "="*70)
    print("AMC Clinical Exam Simulation - Architecture Diagram Generator")
    print("="*70 + "\n")

    print(f"Output directory: {OUTPUT_DIR}\n")

    # Generate all diagrams
    diagram_01_system_architecture_4layer()
    diagram_02_data_flow_osce_session()
    diagram_03_agent_architecture_overview()
    diagram_04_sim001_ai_patient_detail()
    diagram_05_sim002_examiner_detail()
    diagram_06_sim003_orchestrator_detail()
    diagram_07_state_machine_session()
    diagram_08_state_machine_emotions()
    diagram_09_database_schema_er()
    diagram_10_websocket_protocol()
    diagram_11_deployment_architecture()
    diagram_12_integration_architecture()

    print("\n" + "="*70)
    print("✓ All 12 diagrams generated successfully!")
    print(f"✓ Saved to: {OUTPUT_DIR}")
    print("="*70 + "\n")

    # List generated files
    print("Generated files:")
    for i in range(1, 13):
        filename = f"{i:02d}_*.png"
        print(f"  - {filename}")

    print("\nNext steps:")
    print("  1. Review diagrams in the images/ folder")
    print("  2. Generate markdown documentation with embedded diagrams")
    print("  3. Update README.md with architecture overview")


if __name__ == "__main__":
    main()
