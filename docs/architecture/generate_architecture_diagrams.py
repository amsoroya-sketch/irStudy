#!/usr/bin/env python3
"""
Medical Expert System - Architecture Diagram Generator

Generates formal architecture diagrams following Microsoft Development Project standards.
Uses the Python diagrams library to create C4 model architecture diagrams.

Author: irStudy Development Team
Date: 2026-01-18
Version: 1.0.0
"""

import os
from pathlib import Path
from diagrams import Diagram, Cluster, Edge
from diagrams.custom import Custom
from diagrams.programming.framework import FastAPI
from diagrams.programming.language import Python
from diagrams.onprem.database import PostgreSQL
from diagrams.onprem.inmemory import Redis
from diagrams.onprem.analytics import Spark
from diagrams.onprem.client import Client
from diagrams.onprem.compute import Server
from diagrams.onprem.network import Nginx
from diagrams.saas.chat import Slack
from diagrams.generic.database import SQL
from diagrams.generic.storage import Storage
from diagrams.aws.ml import Sagemaker
from diagrams.programming.flowchart import Document


def generate_c4_context_diagram():
    """
    C4 Model - Level 1: System Context Diagram
    Shows the system in the context of users and external systems.
    """
    output_path = Path(__file__).parent / "images"
    output_path.mkdir(exist_ok=True)

    graph_attr = {
        "fontsize": "14",
        "bgcolor": "white",
        "pad": "0.5",
        "splines": "ortho",
    }

    with Diagram(
        "C4 Context - Medical Expert System",
        filename=str(output_path / "01_c4_context_diagram"),
        outformat="png",
        show=False,
        direction="TB",
        graph_attr=graph_attr
    ):
        # External Users
        medical_student = Client("Medical Students\n& IMGs")
        medical_educator = Client("Medical\nEducators")
        clinician = Client("Clinicians\n(Decision Support)")

        # Main System
        with Cluster("Medical Expert System"):
            system = Server("AI-Powered Medical\nEducation Platform\n\n• 10 Specialist Agents\n• MCQ/OSCE Generation\n• Clinical Decision Support")

        # External Systems
        with Cluster("External Medical Knowledge Sources"):
            ncbi = Storage("NCBI StatPearls\n(10,000+ articles)")
            therapeutic_guidelines = SQL("Therapeutic Guidelines\n(eTG) Database\n(9,672 chunks)")
            cochrane = Storage("Cochrane Library\n(Systematic Reviews)")
            racgp = Document("RACGP Red Book\n(Australian Guidelines)")

        with Cluster("AI/ML Services"):
            openai = Sagemaker("OpenAI GPT-4o\n(Vision & Text)")
            anthropic = Sagemaker("Anthropic Claude\n(Clinical Reasoning)")
            google = Sagemaker("Google Gemini\n(Multimodal)")

        # Relationships
        medical_student >> Edge(label="Study materials,\npractice exams") >> system
        medical_educator >> Edge(label="Generate\nassessments") >> system
        clinician >> Edge(label="Clinical decision\nsupport") >> system

        system >> Edge(label="Weekly updates") >> ncbi
        system >> Edge(label="RAG queries") >> therapeutic_guidelines
        system >> Edge(label="Evidence-based\nreviews") >> cochrane
        system >> Edge(label="Australian\nstandards") >> racgp

        system >> Edge(label="Complex reasoning,\nimage interpretation") >> openai
        system >> Edge(label="Clinical reasoning") >> anthropic
        system >> Edge(label="Multimodal tasks") >> google


def generate_c4_container_diagram():
    """
    C4 Model - Level 2: Container Diagram
    Shows the high-level technology choices and how containers communicate.
    """
    output_path = Path(__file__).parent / "images"

    graph_attr = {
        "fontsize": "14",
        "bgcolor": "white",
        "pad": "0.5",
        "splines": "ortho",
    }

    with Diagram(
        "C4 Container - System Architecture",
        filename=str(output_path / "02_c4_container_diagram"),
        outformat="png",
        show=False,
        direction="LR",
        graph_attr=graph_attr
    ):
        user = Client("Users\n(Web Browser)")

        with Cluster("Application Layer"):
            with Cluster("Medical Expert Agents"):
                agent_med001 = Python("MED-001\nCardiology")
                agent_med002 = Python("MED-002\nRespiratory")
                agent_med003 = Python("MED-003\nGastro")
                agent_med010 = Python("MED-010\nGeneral Practice")
                agent_others = Python("MED-004 to MED-009\n(6 other specialists)")

            router = FastAPI("Model Router\n(Python)\n\nIntelligent routing\nbased on complexity")

        with Cluster("AI/ML Integration Layer"):
            local_models = Server("Local Models\n(Ollama)\n\n• Meditron 7B\n• Llama 3.1 8B")
            api_clients = Server("API Clients\n(Python)\n\n• OpenAI Client\n• Anthropic Client\n• Google Client")
            usage_tracker = Redis("Usage Tracker\n(Redis)\n\nCost monitoring\nBudget alerts")

        with Cluster("Knowledge & Data Layer"):
            vector_db = PostgreSQL("Qdrant Vector DB\n\n9,672 eTG chunks\n375 MB")
            resource_db = SQL("Resource Metadata\n(SQLite)\n\n12 tracked resources")
            download_mgr = Storage("Download Manager\n\nWeekly auto-updates\nCrash-safe resume")

        # User interactions
        user >> Edge(label="HTTPS") >> router

        # Agent communication
        router >> Edge(label="Route request") >> agent_med001
        router >> Edge(label="Route request") >> agent_med002
        router >> Edge(label="Route request") >> agent_med003
        router >> Edge(label="Route request") >> agent_med010
        router >> Edge(label="Route request") >> agent_others

        # Model routing
        agent_med001 >> Edge(label="Simple tasks") >> local_models
        agent_med001 >> Edge(label="Complex tasks") >> api_clients
        agent_med002 >> Edge(label="Image analysis") >> api_clients

        # Knowledge access
        agent_med001 >> Edge(label="RAG queries") >> vector_db
        agent_med002 >> Edge(label="RAG queries") >> vector_db
        api_clients >> Edge(label="Log usage") >> usage_tracker

        # Data management
        download_mgr >> Edge(label="Update") >> resource_db
        download_mgr >> Edge(label="Index") >> vector_db


def generate_component_diagram():
    """
    C4 Model - Level 3: Component Diagram
    Shows the components within a container and their interactions.
    """
    output_path = Path(__file__).parent / "images"

    graph_attr = {
        "fontsize": "12",
        "bgcolor": "white",
        "pad": "0.5",
        "splines": "ortho",
    }

    with Diagram(
        "Component Diagram - Medical Expert Agent",
        filename=str(output_path / "03_component_diagram_agent"),
        outformat="png",
        show=False,
        direction="TB",
        graph_attr=graph_attr
    ):
        with Cluster("BaseMedicalExpert (Abstract Base Class)"):
            with Cluster("Core Components"):
                task_executor = Python("Task Executor\n\nExecutes agent tasks")
                tool_registry = Python("Tool Registry\n\nManages specialist tools")
                validator = Python("Output Validator\n\nAustralian compliance\nCitation checking")

            with Cluster("Clinical Reasoning Modules"):
                differential_dx = Python("Differential\nDiagnosis Generator")
                risk_stratifier = Python("Risk Stratification\nCalculator")
                red_flag_detector = Python("Red Flag Detector\n\nLife-threatening\nconditions")

            with Cluster("Content Generation"):
                mcq_generator = Python("MCQ Generator\n\nAMC-compliant format")
                osce_generator = Python("OSCE Generator\n\n8-minute stations\nwith rubrics")

            with Cluster("Knowledge Integration"):
                rag_client = Python("RAG Client\n\nQuery vector DB")
                citation_tracker = Python("Citation Tracker\n\nPage/section numbers")
                australian_validator = Python("Australian Standards\nValidator\n\nTerminology, units,\nemergency numbers")

        # Component relationships
        task_executor >> Edge(label="registers") >> tool_registry
        task_executor >> Edge(label="validates") >> validator

        tool_registry >> Edge(label="contains") >> differential_dx
        tool_registry >> Edge(label="contains") >> risk_stratifier
        tool_registry >> Edge(label="contains") >> red_flag_detector
        tool_registry >> Edge(label="contains") >> mcq_generator
        tool_registry >> Edge(label="contains") >> osce_generator

        mcq_generator >> Edge(label="queries") >> rag_client
        osce_generator >> Edge(label="queries") >> rag_client
        rag_client >> Edge(label="tracks") >> citation_tracker

        validator >> Edge(label="uses") >> australian_validator
        validator >> Edge(label="checks") >> citation_tracker


def generate_deployment_diagram():
    """
    Deployment Diagram - Shows physical deployment architecture
    """
    output_path = Path(__file__).parent / "images"

    graph_attr = {
        "fontsize": "14",
        "bgcolor": "white",
        "pad": "0.5",
        "splines": "ortho",
    }

    with Diagram(
        "Deployment Architecture",
        filename=str(output_path / "04_deployment_diagram"),
        outformat="png",
        show=False,
        direction="TB",
        graph_attr=graph_attr
    ):
        with Cluster("User Devices"):
            laptop = Client("Laptop/Desktop\n(Web Browser)")
            mobile = Client("Mobile Device\n(Responsive Web)")

        with Cluster("Development Environment\n(Linux Ubuntu 22.04)"):
            with Cluster("Application Server"):
                web_server = Nginx("Nginx\n(Reverse Proxy)")
                app_server = FastAPI("FastAPI Server\n(Python 3.10+)")

                with Cluster("Agent Processes"):
                    agents = [
                        Python("MED-001"),
                        Python("MED-002"),
                        Python("..."),
                        Python("MED-010")
                    ]

            with Cluster("Local ML Models\n(Ollama)"):
                meditron = Server("Meditron 7B\n(Medical LLM)")
                llama = Server("Llama 3.1 8B\n(General LLM)")

            with Cluster("Data Storage"):
                qdrant = PostgreSQL("Qdrant Vector DB\nPort: 6333\n\n375 MB\n9,672 chunks")
                sqlite = SQL("SQLite\n(Resource Metadata)")
                file_storage = Storage("File System\n\n/mnt/data/medical_resources\n(External Drive)")

        with Cluster("Cloud AI Services"):
            openai_api = Sagemaker("OpenAI API\n\nGPT-4o Vision\n$0.005/image")
            anthropic_api = Sagemaker("Anthropic API\n\nClaude 3.5 Sonnet\n$0.003/1K tokens")
            google_api = Sagemaker("Google API\n\nGemini 1.5 Pro\n$0.00125/1K tokens")

        with Cluster("External Data Sources"):
            ncbi = Storage("NCBI\n(StatPearls API)")
            guidelines = Storage("Australian Guidelines\n(Web Downloads)")

        # Connections
        laptop >> Edge(label="HTTPS") >> web_server
        mobile >> Edge(label="HTTPS") >> web_server

        web_server >> Edge(label="Forward") >> app_server
        app_server >> Edge(label="Execute") >> agents

        agents[0] >> Edge(label="Local inference") >> meditron
        agents[1] >> Edge(label="Local inference") >> llama

        agents[0] >> Edge(label="API calls") >> openai_api
        agents[1] >> Edge(label="API calls") >> anthropic_api
        agents[2] >> Edge(label="API calls") >> google_api

        agents[0] >> Edge(label="RAG queries") >> qdrant
        agents[1] >> Edge(label="Metadata") >> sqlite

        file_storage >> Edge(label="Weekly updates") >> ncbi
        file_storage >> Edge(label="Downloads") >> guidelines
        file_storage >> Edge(label="Index to") >> qdrant


def generate_data_flow_diagram():
    """
    Data Flow Diagram - Shows how data flows through the system
    """
    output_path = Path(__file__).parent / "images"

    graph_attr = {
        "fontsize": "14",
        "bgcolor": "white",
        "pad": "0.5",
        "splines": "ortho",
    }

    with Diagram(
        "Data Flow - MCQ Generation with RAG",
        filename=str(output_path / "05_data_flow_mcq_generation"),
        outformat="png",
        show=False,
        direction="LR",
        graph_attr=graph_attr
    ):
        user_request = Client("User Request\n\n'Generate MCQ on\nacute coronary\nsyndrome'")

        with Cluster("Processing Pipeline"):
            step1 = Python("1. Task Creation\n\nAgentTask(\n  topic='ACS',\n  difficulty='medium'\n)")
            step2 = Python("2. RAG Query\n\nSearch eTG for\n'acute coronary\nsyndrome'")
            step3 = PostgreSQL("3. Vector Search\n\nQdrant finds\nrelevant chunks\n(confidence > 0.65)")
            step4 = Python("4. Content Generation\n\nLLM generates MCQ\nwith retrieved context")
            step5 = Python("5. Citation Extraction\n\nExtract page/section\nfrom RAG results")
            step6 = Python("6. Australian Validation\n\nCheck:\n• paracetamol ✓\n• mmol/L ✓\n• 000 ✓")
            step7 = Python("7. Output Formatting\n\nJSON with:\n• question\n• options\n• answer\n• explanation\n• citations")

        response = Document("MCQ Response\n\nValidated MCQ\nwith eTG citations\n(Section 5.2.1)")

        # Flow
        user_request >> Edge(label="HTTP POST") >> step1
        step1 >> Edge(label="query") >> step2
        step2 >> Edge(label="semantic search") >> step3
        step3 >> Edge(label="top 3 chunks\n+ confidence") >> step4
        step4 >> Edge(label="generated MCQ") >> step5
        step5 >> Edge(label="MCQ + citations") >> step6
        step6 >> Edge(label="validated MCQ") >> step7
        step7 >> Edge(label="JSON") >> response


def generate_all_diagrams():
    """Generate all architecture diagrams"""
    print("Generating C4 Context Diagram...")
    generate_c4_context_diagram()
    print("✓ C4 Context Diagram generated")

    print("\nGenerating C4 Container Diagram...")
    generate_c4_container_diagram()
    print("✓ C4 Container Diagram generated")

    print("\nGenerating Component Diagram...")
    generate_component_diagram()
    print("✓ Component Diagram generated")

    print("\nGenerating Deployment Diagram...")
    generate_deployment_diagram()
    print("✓ Deployment Diagram generated")

    print("\nGenerating Data Flow Diagram...")
    generate_data_flow_diagram()
    print("✓ Data Flow Diagram generated")

    print("\n" + "="*60)
    print("All architecture diagrams generated successfully!")
    print(f"Output location: {Path(__file__).parent / 'images'}")
    print("="*60)


if __name__ == "__main__":
    generate_all_diagrams()
