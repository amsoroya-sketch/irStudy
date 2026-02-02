# LLM System Requirements & Recommendations

**System Analysis Date:** January 17, 2026
**Your Current Hardware:**
- **CPU**: Intel Core i9-14900HX (24 cores, 32 threads) ✅ Excellent
- **RAM**: 32 GB total (7.1 GB available currently) ⚠️ Limited availability
- **GPU**: NVIDIA GeForce RTX 4070 Laptop (8 GB VRAM) ⚠️ **BOTTLENECK**
- **Storage**: 401 GB total (16 GB free, 96% used) ⚠️ **CRITICAL**

---

## 🎯 Summary: Can Your System Run the Proposed LLMs?

| Model | Size | RAM Needed | VRAM Needed | Your System | Verdict |
|-------|------|------------|-------------|-------------|---------|
| **Meditron 7B** (Q4) | 4.1 GB | 6 GB | 0 GB (CPU) | ✅ | **YES - CPU mode** |
| **Meditron 7B** (Q8) | 7.7 GB | 10 GB | 0 GB (CPU) | ⚠️ | **Marginal - CPU mode** |
| **MedGemma 27B** (Q4) | 16 GB | 20 GB | 0 GB (CPU) | ❌ | **NO - Insufficient RAM** |
| **MedGemma 27B** (Q4) | - | - | 16 GB (GPU) | ❌ | **NO - GPU only 8GB** |
| **Llama 3.1 70B** (Q4) | 40 GB | 48 GB | 0 GB (CPU) | ❌ | **NO - Way too large** |
| **Llama 3.3 70B** (Q2) | 26 GB | 32 GB | 0 GB (CPU) | ❌ | **NO - Barely fits, would swap** |

**VERDICT:** ⚠️ Your current system **CANNOT** run the proposed large models (MedGemma 27B, Llama 70B) due to:
1. **Insufficient GPU VRAM** (need 24-32 GB, have 8 GB)
2. **Insufficient RAM** (need 32-64 GB free, have 7 GB available)
3. **Critically low disk space** (96% full)

---

## ✅ What You CAN Run (Recommended for Your System)

### Option 1: Meditron 7B (Quantized Q4) - **RECOMMENDED**

**Why This Works:**
- Small enough for your system (4-5 GB RAM needed)
- Medical-specific training (better than general models)
- Runs on CPU (doesn't need GPU)
- Good performance for medical Q&A

**Specifications:**
- Model Size: ~4.1 GB (Q4 quantization)
- RAM Required: 6-8 GB
- VRAM Required: 0 GB (CPU inference)
- Speed: 20-40 tokens/second (CPU)
- Medical Accuracy: 60% on MedQA benchmark

**Installation:**
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull Meditron 7B
ollama pull meditron:7b

# Test it
ollama run meditron:7b "What is the first-line treatment for community-acquired pneumonia in Australia?"
```

### Option 2: Llama 3.1 8B (Quantized Q4) - **ALTERNATIVE**

**Why Consider This:**
- Newer architecture (2024 vs 2023)
- Better general reasoning
- Similar size to Meditron 7B
- Not medical-specific, but more capable

**Specifications:**
- Model Size: ~4.7 GB (Q4 quantization)
- RAM Required: 8 GB
- VRAM Required: 0 GB (CPU inference)
- Speed: 20-30 tokens/second (CPU)
- Medical Accuracy: ~55% on MedQA (not medical-trained)

**Installation:**
```bash
ollama pull llama3.1:8b
ollama run llama3.1:8b
```

### Option 3: Hybrid Approach - **BEST COMPROMISE**

Use **local small models for simple tasks** + **API calls for complex tasks**:

**Local Models (Your System):**
- Meditron 7B for medical Q&A (4 GB)
- Llama 3.1 8B for general reasoning (5 GB)

**API Models (Cloud):**
- GPT-4 for complex clinical reasoning ($0.01/1K tokens)
- Claude Sonnet for long-context analysis ($0.003/1K tokens)
- Med-PaLM 2 for specialized medical tasks (Google Cloud)

**Cost Estimate:**
- 1,000 MCQs generated: ~$5-10 (mostly local, API for validation)
- Much cheaper than buying new hardware

---

## ❌ What You CANNOT Run

### MedGemma 27B - **TOO LARGE**

**Why It Won't Work:**
- Needs 16-20 GB RAM (you have 7 GB available)
- Needs 16-20 GB VRAM for GPU (you have 8 GB total, 3.8 GB free)
- Even with quantization, needs 12+ GB VRAM

**To Run This, You'd Need:**
- NVIDIA RTX 4090 (24 GB VRAM) - $1,600
- Or NVIDIA RTX A6000 (48 GB VRAM) - $4,500
- Or rent cloud GPU (A100 80GB) - $1-3/hour

### Llama 3.1 70B - **WAY TOO LARGE**

**Why It Won't Work:**
- Needs 40-80 GB RAM (you have 32 GB total)
- Needs 40-80 GB VRAM for GPU (you have 8 GB)
- Even heavily quantized (Q2), needs 26 GB

**To Run This, You'd Need:**
- 128 GB RAM workstation - $2,000+
- NVIDIA A100 80GB - $10,000+
- Or cloud rental - $2-5/hour

---

## 🔧 System Upgrade Recommendations

### Priority 1: Free Up RAM (Immediate, $0)

**Current RAM Usage:**
- Total: 32 GB
- Used: 24 GB
- Available: **7.1 GB** ← TOO LOW

**Free Up RAM:**
```bash
# Close VirtualBox VM (using 2.7 GB GPU + RAM)
# Current VM usage: 2737 MB GPU memory

# Check what's using RAM
ps aux --sort=-%mem | head -20

# Kill unnecessary processes
# Close Firefox tabs (using memory)
# Close unnecessary applications
```

**Target:** Get 16+ GB free RAM for better LLM performance

### Priority 2: Free Up Disk Space (Immediate, $0)

**Current Status:**
- Used: 366 GB / 401 GB (96% full) ⚠️ **CRITICAL**
- Free: **16 GB** ← Need 50+ GB for medical resources

**Free Up Space:**
```bash
# Find large files
du -sh /* 2>/dev/null | sort -rh | head -20
du -sh ~/.cache/* 2>/dev/null | sort -rh | head -10

# Clear package cache
sudo apt clean
sudo apt autoremove

# Clear old Docker images/containers
docker system prune -a

# Clear Snap cache
rm -rf ~/snap/*/common/.cache
sudo snap set system refresh.retain=2

# Clear browser cache
rm -rf ~/.cache/mozilla
rm -rf ~/.cache/google-chrome

# Target: Free 50+ GB for medical resources
```

### Priority 3: Upgrade RAM (Optional, $100-200)

**Current:** 32 GB RAM
**Recommended:** 64 GB RAM

**Why:** Would allow running MedGemma 27B on CPU (slower but functional)

**Cost:** ~$100-200 for 32 GB additional laptop RAM (if slots available)

**Check if possible:**
```bash
sudo dmidecode --type memory | grep -E "Size|Type:|Speed:"
# Check if you have free RAM slots
```

### Priority 4: External GPU (Optional, $500-1,500)

**Current:** RTX 4070 Laptop (8 GB VRAM)
**Recommended:** RTX 4090 (24 GB VRAM)

**Options:**
1. **Thunderbolt eGPU Enclosure** + RTX 4090
   - Cost: ~$300 (enclosure) + $1,600 (GPU) = $1,900
   - Requires: Thunderbolt 4 port (check if your laptop has one)

2. **Rent Cloud GPU** (More practical)
   - NVIDIA A100 (40GB): $1.10/hour
   - NVIDIA H100 (80GB): $2-3/hour
   - Use only when needed (cheaper than buying hardware)

**Check Thunderbolt:**
```bash
lspci | grep -i thunderbolt
# If found, eGPU is possible
```

---

## 💡 Recommended Strategy for Your System

### Phase 1: Optimize Current System (This Week, $0)

1. **Free Up RAM:**
   - Close VirtualBox VM (saves 3+ GB)
   - Close unnecessary browser tabs
   - Target: 16+ GB free RAM

2. **Free Up Disk Space:**
   - Clear caches and old files
   - Target: 50+ GB free for medical resources

3. **Use Meditron 7B (Q4):**
   - Install: `ollama pull meditron:7b`
   - RAM needed: 6-8 GB (fits your system)
   - Good medical accuracy (60% MedQA)

### Phase 2: Hybrid Approach (Ongoing)

**Local Models (Free):**
- Meditron 7B for medical Q&A
- Llama 3.1 8B for general text

**Cloud API (Pay-per-use):**
- GPT-4 for complex reasoning (~$5-10/month for your use case)
- Claude Sonnet for long context
- Use local models first, API only when needed

**Cost Estimate:**
- Generate 1,000 MCQs: ~$10-20 total
- Much cheaper than hardware upgrades

### Phase 3: Future Hardware (Optional, if budget allows)

**Option A: Upgrade Laptop RAM to 64 GB** ($100-200)
- Allows running MedGemma 27B on CPU (slow but works)
- Check if your laptop supports 64 GB

**Option B: Build Desktop Workstation** ($2,000-3,000)
- 64-128 GB RAM
- NVIDIA RTX 4090 (24 GB VRAM)
- 2 TB NVMe SSD
- Can run Llama 3.1 70B smoothly

**Option C: Use Cloud GPUs** ($50-100/month)
- Rent A100 GPUs only when generating content
- More flexible than buying hardware
- Scale up/down as needed

---

## 📊 Performance Comparison Table

### Models You CAN Run on Your System

| Model | Size | RAM | Speed (CPU) | Medical Score | Best For |
|-------|------|-----|-------------|---------------|----------|
| Meditron 7B Q4 | 4 GB | 6 GB | 30 tok/s | 60% MedQA | Medical Q&A ✅ |
| Llama 3.1 8B Q4 | 5 GB | 8 GB | 25 tok/s | 55% MedQA | General reasoning ✅ |
| Llama 3.3 70B Q2 | 26 GB | 32 GB | 2-5 tok/s | 75% MedQA | Complex reasoning ⚠️ (would swap heavily) |

### Models You CANNOT Run

| Model | Size | RAM | VRAM | Why Not? |
|-------|------|-----|------|----------|
| MedGemma 27B Q4 | 16 GB | 20 GB | 16 GB | Need 24 GB GPU, you have 8 GB |
| Llama 3.1 70B Q4 | 40 GB | 48 GB | 40 GB | Need 64+ GB RAM, you have 32 GB |
| Med-PaLM 2 | Cloud | Cloud | Cloud | Google Cloud only, $$ per call |

### Cloud API Options (Recommended)

| API | Cost | Medical | Speed | Best For |
|-----|------|---------|-------|----------|
| GPT-4o | $0.005/1K tok | Good | Fast | Complex reasoning ✅ |
| Claude Sonnet | $0.003/1K tok | Good | Fast | Long context ✅ |
| Claude Haiku | $0.00025/1K tok | OK | Very Fast | Simple tasks ✅ |
| Gemini 1.5 Pro | $0.00125/1K tok | Good | Fast | Multimodal ✅ |

---

## 🎯 Final Recommendation

### For Your Current System (No Upgrades)

**Use This Stack:**

1. **Primary Model: Meditron 7B (Q4)** - Free, local
   - Medical Q&A
   - MCQ option generation
   - Simple clinical queries

2. **Secondary Model: Llama 3.1 8B (Q4)** - Free, local
   - General text generation
   - Explanations and reasoning

3. **Cloud API: Claude Haiku** - $0.00025/1K tokens
   - Complex clinical reasoning
   - Multi-step problem solving
   - Quality validation

4. **Validation: GPT-4o** - $0.005/1K tokens
   - Final quality check
   - Citation verification
   - Critical medical accuracy

**Estimated Monthly Cost:** $10-30 for generating 1,000+ MCQs

**Why This Works:**
- ✅ 80% of work done locally (free)
- ✅ 20% of complex work via API (cheap)
- ✅ No hardware upgrades needed
- ✅ Scales with your usage
- ✅ Better results than struggling with too-large local models

### If You Upgrade (Optional)

**Upgrade Path 1: RAM to 64 GB** ($100-200)
- Can run MedGemma 27B on CPU (slow but works)
- Better than APIs for high-volume generation
- ROI: If generating 10,000+ MCQs

**Upgrade Path 2: Desktop Workstation** ($2,500)
- 64 GB RAM + RTX 4090 (24 GB VRAM)
- Run Llama 3.1 70B smoothly
- Run MedGemma 27B on GPU (fast)
- ROI: If this is long-term profession/business

**Upgrade Path 3: Cloud Compute** ($50-100/month)
- Rent GPU when needed
- A100 40GB: $1.10/hour
- Most flexible option
- ROI: Varies by usage

---

## 🚀 Quick Start Commands

### Install Recommended Local Models

```bash
# Install Ollama (if not already installed)
curl -fsSL https://ollama.com/install.sh | sh

# Pull Meditron 7B (medical-specific)
ollama pull meditron:7b

# Pull Llama 3.1 8B (general purpose)
ollama pull llama3.1:8b

# Test Meditron
ollama run meditron:7b "What is the first-line treatment for community-acquired pneumonia in Australia per Therapeutic Guidelines?"

# Test Llama
ollama run llama3.1:8b "Explain the pathophysiology of acute coronary syndrome"
```

### Check Available Resources

```bash
# Check RAM availability
free -h

# Check GPU memory
nvidia-smi

# Check disk space
df -h

# List running Ollama models
ollama list

# Remove unused models to save space
ollama rm <model-name>
```

### Model Router Configuration

```python
# In your medical agents, use this router logic:

def select_model(query_complexity: str, query_type: str):
    """
    Smart model selection based on task complexity.

    Simple queries → Meditron 7B (local, free, fast)
    Complex queries → Claude Haiku (API, cheap, accurate)
    Critical validation → GPT-4o (API, expensive, most accurate)
    """

    if query_complexity == "simple":
        return "ollama/meditron:7b"  # Local, free
    elif query_complexity == "medium":
        return "ollama/llama3.1:8b"  # Local, free
    elif query_complexity == "complex":
        return "claude/haiku"  # API, $0.00025/1K tokens
    else:  # Critical medical accuracy needed
        return "openai/gpt-4o"  # API, $0.005/1K tokens
```

---

## 📞 Action Items

### Immediate (Today)

1. **Free up RAM:**
   ```bash
   # Stop VirtualBox VM
   # Close unnecessary applications
   # Target: 16+ GB free
   ```

2. **Free up disk space:**
   ```bash
   sudo apt clean
   docker system prune -a
   # Target: 50+ GB free
   ```

3. **Install Meditron 7B:**
   ```bash
   ollama pull meditron:7b
   ollama run meditron:7b
   ```

### This Week

1. Test Meditron 7B with medical queries
2. Benchmark performance (tokens/second)
3. Compare with API models (quality vs cost)
4. Decide: Local-only vs Hybrid approach

### Future (Optional)

1. Check if laptop supports 64 GB RAM
2. Research cloud GPU pricing
3. Evaluate ROI for hardware upgrades

---

## ✅ Summary

**Your Current System:**
- ✅ Can run: Meditron 7B, Llama 3.1 8B (local, free)
- ❌ Cannot run: MedGemma 27B, Llama 70B (too large)
- ⚠️ System limitations: 8 GB GPU, low free RAM/disk

**Best Strategy:**
- Use Meditron 7B locally (free, medical-specific)
- Use Claude Haiku API for complex tasks (cheap)
- Use GPT-4o for validation (expensive but accurate)
- **Cost:** $10-30/month vs $2,000+ hardware upgrade

**Bottom Line:** Your system is adequate for the medical agent project using a hybrid local+API approach. No immediate hardware upgrades needed!

---

**Last Updated:** January 17, 2026
**Status:** ✅ Recommendations Ready
**Next:** Free up resources, install Meditron 7B, test performance
