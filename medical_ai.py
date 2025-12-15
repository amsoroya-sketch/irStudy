#!/usr/bin/env python3
"""
Medical Education AI - Command Line Interface
Main entry point for managing the system
"""

import click
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))


@click.group()
@click.version_option(version='0.1.0')
def cli():
    """
    Medical Education AI System - CLI Tool

    AI-powered platform for ICRP, AMC MCQ, and AMC Clinical preparation.
    Uses local LLMs, RAG, and multi-agent systems for unlimited content generation.
    """
    pass


@cli.group()
def process():
    """Process medical textbooks and build knowledge base"""
    pass


@process.command('pdfs')
@click.option('--input', default='data/pdfs', help='Input directory with PDFs')
@click.option('--output', default='data/processed', help='Output directory for extracted text')
def extract_pdfs(input, output):
    """Extract text from medical textbook PDFs"""
    from scripts.extract_pdfs import MedicalPDFExtractor

    click.echo(click.style('📚 Extracting PDFs...', fg='blue', bold=True))
    extractor = MedicalPDFExtractor(output_dir=output)
    extractor.process_all_pdfs(pdf_dir=input)
    click.echo(click.style('✓ PDF extraction complete!', fg='green', bold=True))


@process.command('chunk')
@click.option('--input', default='data/processed', help='Input directory with extracted JSONs')
@click.option('--output', default='data/chunks.json', help='Output file for chunks')
@click.option('--chunk-size', default=1000, help='Target chunk size in tokens')
@click.option('--overlap', default=150, help='Overlap between chunks')
def chunk_texts(input, output, chunk_size, overlap):
    """Chunk medical texts intelligently"""
    from scripts.chunk_medical_texts import MedicalTextChunker

    click.echo(click.style('✂️  Chunking medical texts...', fg='blue', bold=True))
    chunker = MedicalTextChunker(chunk_size=chunk_size, overlap=overlap)
    chunker.process_all_books(input_dir=input, output_file=output)
    click.echo(click.style('✓ Text chunking complete!', fg='green', bold=True))


@process.command('embed')
@click.option('--input', default='data/chunks.json', help='Input chunks file')
@click.option('--output', default='data/embeddings/medical_embeddings.pkl', help='Output embeddings file')
@click.option('--model', default='pritamdeka/S-PubMedBert-MS-MARCO', help='Embedding model')
@click.option('--batch-size', default=32, help='Batch size for GPU')
def generate_embeddings(input, output, model, batch_size):
    """Generate PubMedBERT embeddings"""
    from scripts.generate_embeddings import MedicalEmbeddingGenerator

    click.echo(click.style('🧠 Generating embeddings...', fg='blue', bold=True))
    generator = MedicalEmbeddingGenerator(model_name=model)
    generator.process_chunks(chunks_file=input, output_file=output, batch_size=batch_size)
    click.echo(click.style('✓ Embedding generation complete!', fg='green', bold=True))


@process.command('index')
@click.option('--embeddings', default='data/embeddings/medical_embeddings.pkl', help='Embeddings file')
@click.option('--collection', default='medical_knowledge', help='Qdrant collection name')
@click.option('--qdrant-url', default='http://localhost:6333', help='Qdrant URL')
@click.option('--batch-size', default=100, help='Upload batch size')
def index_qdrant(embeddings, collection, qdrant_url, batch_size):
    """Index embeddings in Qdrant"""
    from scripts.index_qdrant import QdrantIndexer

    click.echo(click.style('💾 Indexing in Qdrant...', fg='blue', bold=True))
    indexer = QdrantIndexer(qdrant_url=qdrant_url)
    indexer.upload_embeddings(embeddings_file=embeddings, collection_name=collection, batch_size=batch_size)
    click.echo(click.style('✓ Qdrant indexing complete!', fg='green', bold=True))


@process.command('all')
@click.confirmation_option(prompt='This will process all PDFs and may take several hours. Continue?')
def process_all():
    """Run complete processing pipeline (PDFs → Chunks → Embeddings → Index)"""
    import subprocess

    steps = [
        ('Extracting PDFs', ['python', 'scripts/extract_pdfs.py']),
        ('Chunking texts', ['python', 'scripts/chunk_medical_texts.py']),
        ('Generating embeddings', ['python', 'scripts/generate_embeddings.py']),
        ('Indexing Qdrant', ['python', 'scripts/index_qdrant.py']),
    ]

    for step_name, command in steps:
        click.echo(click.style(f'\n▶ {step_name}...', fg='blue', bold=True))
        result = subprocess.run(command)
        if result.returncode != 0:
            click.echo(click.style(f'✗ {step_name} failed!', fg='red', bold=True))
            return
        click.echo(click.style(f'✓ {step_name} complete!', fg='green', bold=True))

    click.echo(click.style('\n🎉 All processing complete!', fg='green', bold=True))


@cli.group()
def test():
    """Test system components"""
    pass


@test.command('llm')
@click.option('--model', default='meditron:7b', help='Ollama model to test')
def test_llm(model):
    """Test local LLM integration"""
    from src.models.ollama_client import OllamaClient

    click.echo(click.style(f'🤖 Testing {model}...', fg='blue', bold=True))

    client = OllamaClient()
    response = client.generate(
        prompt="What are the symptoms of acute coronary syndrome? List 5 key symptoms.",
        model_name=model
    )

    click.echo(click.style('\nResponse:', fg='yellow'))
    click.echo(response)
    click.echo(click.style('\n✓ LLM test complete!', fg='green', bold=True))


@test.command('search')
@click.argument('query')
@click.option('--limit', default=5, help='Number of results')
@click.option('--collection', default='medical_knowledge', help='Collection name')
def test_search(query, limit, collection):
    """Test semantic search in Qdrant"""
    from qdrant_client import QdrantClient
    from sentence_transformers import SentenceTransformer

    click.echo(click.style(f'🔍 Searching for: "{query}"', fg='blue', bold=True))

    # Connect
    client = QdrantClient(url='http://localhost:6333')
    model = SentenceTransformer('pritamdeka/S-PubMedBert-MS-MARCO')

    # Search
    query_vec = model.encode(query).tolist()
    results = client.search(
        collection_name=collection,
        query_vector=query_vec,
        limit=limit
    )

    click.echo(click.style(f'\nTop {limit} results:', fg='yellow'))
    for i, result in enumerate(results, 1):
        click.echo(f'\n{i}. Score: {result.score:.4f}')
        click.echo(f'   Source: {result.payload["source"]} (page {result.payload["page"]})')
        click.echo(f'   Text: {result.payload["text"][:200]}...')

    click.echo(click.style('\n✓ Search test complete!', fg='green', bold=True))


@cli.group()
def services():
    """Manage Docker services"""
    pass


@services.command('start')
def start_services():
    """Start all Docker services"""
    import subprocess

    click.echo(click.style('🚀 Starting Docker services...', fg='blue', bold=True))
    result = subprocess.run(['docker-compose', 'up', '-d'])

    if result.returncode == 0:
        click.echo(click.style('✓ All services started!', fg='green', bold=True))
        subprocess.run(['docker-compose', 'ps'])
    else:
        click.echo(click.style('✗ Failed to start services', fg='red', bold=True))


@services.command('stop')
def stop_services():
    """Stop all Docker services"""
    import subprocess

    click.echo(click.style('🛑 Stopping Docker services...', fg='blue', bold=True))
    result = subprocess.run(['docker-compose', 'down'])

    if result.returncode == 0:
        click.echo(click.style('✓ All services stopped!', fg='green', bold=True))
    else:
        click.echo(click.style('✗ Failed to stop services', fg='red', bold=True))


@services.command('status')
def service_status():
    """Check status of all services"""
    import subprocess

    click.echo(click.style('📊 Service Status:', fg='blue', bold=True))
    subprocess.run(['docker-compose', 'ps'])


@services.command('logs')
@click.argument('service', required=False)
@click.option('--follow', '-f', is_flag=True, help='Follow log output')
def service_logs(service, follow):
    """View service logs"""
    import subprocess

    cmd = ['docker-compose', 'logs']
    if follow:
        cmd.append('-f')
    if service:
        cmd.append(service)

    subprocess.run(cmd)


@cli.command('info')
def system_info():
    """Show system information"""
    import subprocess
    import torch

    click.echo(click.style('📋 System Information', fg='blue', bold=True))
    click.echo()

    # Python version
    click.echo(f'Python: {sys.version.split()[0]}')

    # CUDA
    cuda_available = torch.cuda.is_available()
    if cuda_available:
        click.echo(f'CUDA: Available (Device: {torch.cuda.get_device_name(0)})')
    else:
        click.echo('CUDA: Not available')

    # Ollama models
    click.echo('\nOllama Models:')
    result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
    if result.returncode == 0:
        click.echo(result.stdout)

    # Docker services
    click.echo('Docker Services:')
    subprocess.run(['docker-compose', 'ps'])

    # Qdrant collections
    try:
        from qdrant_client import QdrantClient
        client = QdrantClient(url='http://localhost:6333')
        collections = client.get_collections().collections
        click.echo('\nQdrant Collections:')
        for col in collections:
            info = client.get_collection(collection_name=col.name)
            click.echo(f'  - {col.name}: {info.points_count:,} points')
    except Exception as e:
        click.echo(f'\nQdrant: Not accessible ({e})')


@cli.command('setup')
def run_setup():
    """Run initial setup"""
    import subprocess

    click.echo(click.style('🔧 Running setup...', fg='blue', bold=True))
    result = subprocess.run(['bash', 'setup.sh'])

    if result.returncode == 0:
        click.echo(click.style('\n✓ Setup complete!', fg='green', bold=True))
    else:
        click.echo(click.style('\n✗ Setup failed!', fg='red', bold=True))


if __name__ == '__main__':
    cli()
