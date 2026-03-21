#!/usr/bin/env tsx
/**
 * Import irStudy Production Launch PRDs into Ralph Dashboard
 *
 * This script imports all 21 production-launch PRDs into the Ralph Dashboard
 * database, creating the irStudy project and associated user stories with
 * proper agent assignments.
 *
 * Usage:
 *   cd /home/dev/Development/ralph-dashboard
 *   npx tsx /home/dev/Development/irStudy/scripts/import_prds_to_ralph_dashboard.ts
 */

import { PrismaClient } from '@prisma/client';
import { PrismaLibSql } from '@prisma/adapter-libsql';
import { createClient } from '@libsql/client';
import fs from 'fs';
import path from 'path';

// Change to ralph-dashboard directory
const dashboardRoot = '/home/dev/Development/ralph-dashboard';
process.chdir(dashboardRoot);

const dbPath = path.join(dashboardRoot, 'dev.db');
const dbUrl = `file:${dbPath}`;
console.log(`Using database at: ${dbUrl}`);

const libsql = createClient({ url: dbUrl });
const adapter = new PrismaLibSql(libsql);
const prisma = new PrismaClient({
  adapter,
  log: ['info', 'warn', 'error'],
});

// PRD metadata with agent assignments
const prdMetadata = [
  // Phase 1: Frontend Core (8-10h each)
  {
    id: 'PRD-PHASE1-001-WEBSOCKET-CHAT-UI',
    featureName: 'WebSocket Chat Interface for AI OSCE Sessions',
    filePath: '/home/dev/Development/irStudy/production-launch-prds/phase1-frontend/PRD-PHASE1-001-WEBSOCKET-CHAT-UI.md',
    agent: 'flutter-desktop-expert',
    priority: 1,
    estimatedHours: 9,
    phase: 1,
    riskLevel: 'HIGH' as const,
  },
  {
    id: 'PRD-PHASE1-002-SESSION-CONTROLS',
    featureName: 'OSCE Session Controls (Timer, Start/Stop, Emergency Exit)',
    filePath: '/home/dev/Development/irStudy/production-launch-prds/phase1-frontend/PRD-PHASE1-002-SESSION-CONTROLS.md',
    agent: 'flutter-desktop-expert',
    priority: 2,
    estimatedHours: 9,
    phase: 1,
    riskLevel: 'HIGH' as const,
  },
  {
    id: 'PRD-PHASE1-003-EMOTIONAL-STATE-UI',
    featureName: 'AI Patient Emotional State Visualization',
    filePath: '/home/dev/Development/irStudy/production-launch-prds/phase1-frontend/PRD-PHASE1-003-EMOTIONAL-STATE-UI.md',
    agent: 'flutter-desktop-expert',
    priority: 3,
    estimatedHours: 8,
    phase: 1,
    riskLevel: 'MEDIUM' as const,
  },

  // Phase 2: Scoring System (6-8h each)
  {
    id: 'PRD-PHASE2-001-SCORING-INTEGRATION',
    featureName: 'AI Examiner Scoring Integration (AMC 15-Mark Rubric)',
    filePath: '/home/dev/Development/irStudy/production-launch-prds/phase2-scoring/PRD-PHASE2-001-SCORING-INTEGRATION.md',
    agent: 'aba-clinical-expert',
    priority: 4,
    estimatedHours: 7,
    phase: 2,
    riskLevel: 'HIGH' as const,
  },
  {
    id: 'PRD-PHASE2-002-CRITICAL-ERROR-DETECTION',
    featureName: 'Critical Error Detection System (Auto-Fail Scenarios)',
    filePath: '/home/dev/Development/irStudy/production-launch-prds/phase2-scoring/PRD-PHASE2-002-CRITICAL-ERROR-DETECTION.md',
    agent: 'aba-clinical-expert',
    priority: 5,
    estimatedHours: 7,
    phase: 2,
    riskLevel: 'HIGH' as const,
  },
  {
    id: 'PRD-PHASE2-003-FEEDBACK-GENERATION',
    featureName: 'Personalized Feedback Generation (Strengths & Areas to Improve)',
    filePath: '/home/dev/Development/irStudy/production-launch-prds/phase2-scoring/PRD-PHASE2-003-FEEDBACK-GENERATION.md',
    agent: 'aba-clinical-expert',
    priority: 6,
    estimatedHours: 7,
    phase: 2,
    riskLevel: 'MEDIUM' as const,
  },

  // Phase 3: Spaced Repetition (6-8h each)
  {
    id: 'PRD-PHASE3-001-FLASHCARD-INTERFACE',
    featureName: 'Study Card Flashcard Interface with Flip Animation',
    filePath: '/home/dev/Development/irStudy/production-launch-prds/phase3-spaced-repetition/PRD-PHASE3-001-FLASHCARD-INTERFACE.md',
    agent: 'flutter-desktop-expert',
    priority: 7,
    estimatedHours: 7,
    phase: 3,
    riskLevel: 'LOW' as const,
  },
  {
    id: 'PRD-PHASE3-002-SM2-ALGORITHM',
    featureName: 'SuperMemo 2 (SM-2) Spaced Repetition Algorithm',
    filePath: '/home/dev/Development/irStudy/production-launch-prds/phase3-spaced-repetition/PRD-PHASE3-002-SM2-ALGORITHM.md',
    agent: 'rust-ffi-expert',
    priority: 8,
    estimatedHours: 7,
    phase: 3,
    riskLevel: 'MEDIUM' as const,
  },

  // Phase 4: EMR Integration (8-12h each)
  {
    id: 'PRD-PHASE4-001-EMR-DATABASE',
    featureName: 'EMR Database Schema with SQLCipher Encryption',
    filePath: '/home/dev/Development/irStudy/production-launch-prds/phase4-emr/PRD-PHASE4-001-EMR-DATABASE.md',
    agent: 'rust-ffi-expert',
    priority: 9,
    estimatedHours: 10,
    phase: 4,
    riskLevel: 'HIGH' as const,
  },
  {
    id: 'PRD-PHASE4-002-EPIC-UI',
    featureName: 'Epic-Inspired UI Mockup for EMR Practice',
    filePath: '/home/dev/Development/irStudy/production-launch-prds/phase4-emr/PRD-PHASE4-002-EPIC-UI.md',
    agent: 'flutter-desktop-expert',
    priority: 10,
    estimatedHours: 10,
    phase: 4,
    riskLevel: 'MEDIUM' as const,
  },
  {
    id: 'PRD-PHASE4-003-AHPRA-COMPLIANCE',
    featureName: 'AHPRA Compliance Validation Rules',
    filePath: '/home/dev/Development/irStudy/production-launch-prds/phase4-emr/PRD-PHASE4-003-AHPRA-COMPLIANCE.md',
    agent: 'security-compliance-expert',
    priority: 11,
    estimatedHours: 11,
    phase: 4,
    riskLevel: 'HIGH' as const,
  },

  // Phase 5: Content Generation (20-80h total)
  {
    id: 'PRD-PHASE5-001-VIDEO-RAG',
    featureName: 'Video RAG Integration with Qdrant',
    filePath: '/home/dev/Development/irStudy/production-launch-prds/phase5-content/PRD-PHASE5-001-VIDEO-RAG.md',
    agent: 'rust-ffi-expert',
    priority: 12,
    estimatedHours: 12,
    phase: 5,
    riskLevel: 'MEDIUM' as const,
  },
  {
    id: 'PRD-PHASE5-002-BATCH-GENERATION',
    featureName: 'Batch 2-10 Persona Generation (1,863 personas)',
    filePath: '/home/dev/Development/irStudy/production-launch-prds/phase5-content/PRD-PHASE5-002-BATCH-GENERATION.md',
    agent: 'general-purpose',
    priority: 13,
    estimatedHours: 60,
    phase: 5,
    riskLevel: 'MEDIUM' as const,
  },
  {
    id: 'PRD-PHASE5-003-QA-VALIDATION',
    featureName: 'QA Validation Pipeline with Citation Verification',
    filePath: '/home/dev/Development/irStudy/production-launch-prds/phase5-content/PRD-PHASE5-003-QA-VALIDATION.md',
    agent: 'testing-qa-expert',
    priority: 14,
    estimatedHours: 15,
    phase: 5,
    riskLevel: 'HIGH' as const,
  },
  {
    id: 'PRD-PHASE5-004-AUTO-STUDY-CARDS',
    featureName: 'Auto Study Card Generation from Sessions',
    filePath: '/home/dev/Development/irStudy/production-launch-prds/phase5-content/PRD-PHASE5-004-AUTO-STUDY-CARDS.md',
    agent: 'aba-clinical-expert',
    priority: 15,
    estimatedHours: 8,
    phase: 5,
    riskLevel: 'MEDIUM' as const,
  },

  // Phase 6: Mock Exam (16-20h)
  {
    id: 'PRD-PHASE6-001-MOCK-EXAM',
    featureName: '16-Station Mock Exam Orchestration',
    filePath: '/home/dev/Development/irStudy/production-launch-prds/phase6-mock-exam/PRD-PHASE6-001-MOCK-EXAM.md',
    agent: 'general-purpose',
    priority: 16,
    estimatedHours: 18,
    phase: 6,
    riskLevel: 'HIGH' as const,
  },

  // Phase 7: Testing & Security (12-16h each)
  {
    id: 'PRD-PHASE7-001-LOAD-TESTING',
    featureName: 'Load Testing (50 concurrent sessions)',
    filePath: '/home/dev/Development/irStudy/production-launch-prds/phase7-testing/PRD-PHASE7-001-LOAD-TESTING.md',
    agent: 'testing-qa-expert',
    priority: 17,
    estimatedHours: 14,
    phase: 7,
    riskLevel: 'HIGH' as const,
  },
  {
    id: 'PRD-PHASE7-002-E2E-TESTING',
    featureName: 'E2E Testing (Complete OSCE Flow)',
    filePath: '/home/dev/Development/irStudy/production-launch-prds/phase7-testing/PRD-PHASE7-002-E2E-TESTING.md',
    agent: 'testing-qa-expert',
    priority: 18,
    estimatedHours: 14,
    phase: 7,
    riskLevel: 'HIGH' as const,
  },
  {
    id: 'PRD-PHASE7-003-SECURITY-AUDIT',
    featureName: 'Security Audit (OWASP Top 10, PHI Protection)',
    filePath: '/home/dev/Development/irStudy/production-launch-prds/phase7-testing/PRD-PHASE7-003-SECURITY-AUDIT.md',
    agent: 'security-compliance-expert',
    priority: 19,
    estimatedHours: 16,
    phase: 7,
    riskLevel: 'HIGH' as const,
  },

  // Phase 8: UI Polish (4-6h each)
  {
    id: 'PRD-PHASE8-001-NAV-UNIFICATION',
    featureName: 'Navigation Unification (MCQ + OSCE + Study Cards)',
    filePath: '/home/dev/Development/irStudy/production-launch-prds/phase8-polish/PRD-PHASE8-001-NAV-UNIFICATION.md',
    agent: 'flutter-desktop-expert',
    priority: 20,
    estimatedHours: 5,
    phase: 8,
    riskLevel: 'LOW' as const,
  },
  {
    id: 'PRD-PHASE8-002-PROGRESS-DASHBOARD',
    featureName: 'Unified Progress Dashboard',
    filePath: '/home/dev/Development/irStudy/production-launch-prds/phase8-polish/PRD-PHASE8-002-PROGRESS-DASHBOARD.md',
    agent: 'flutter-desktop-expert',
    priority: 21,
    estimatedHours: 5,
    phase: 8,
    riskLevel: 'LOW' as const,
  },
];

async function main() {
  console.log('🚀 Importing irStudy Production Launch PRDs into Ralph Dashboard\n');

  // 1. Find or create default user
  let user = await prisma.user.findUnique({
    where: { email: 'dev@irstudy.local' },
  });

  if (!user) {
    user = await prisma.user.create({
      data: {
        email: 'dev@irstudy.local',
        name: 'irStudy Developer',
        role: 'DEVELOPER',
      },
    });
    console.log('✅ Created default user: dev@irstudy.local');
  } else {
    console.log('✅ Found existing user: dev@irstudy.local');
  }

  // 2. Find or create irStudy project
  let project = await prisma.project.findFirst({
    where: { name: 'irStudy' },
  });

  if (!project) {
    project = await prisma.project.create({
      data: {
        name: 'irStudy',
        description: 'Medical education platform with AI OSCE simulation, EMR practice, and spaced repetition study cards',
        repositoryUrl: 'https://github.com/yourusername/irStudy',
        branchName: 'main',
        status: 'ACTIVE',
        createdByUserId: user.id,
        codebasePath: '/home/dev/Development/irStudy',
      },
    });
    console.log('✅ Created irStudy project\n');
  } else {
    console.log('✅ Found existing irStudy project\n');
  }

  // 3. Ensure expert agents exist
  const agentNames = [
    'flutter-desktop-expert',
    'rust-ffi-expert',
    'security-compliance-expert',
    'testing-qa-expert',
    'aba-clinical-expert',
    'general-purpose',
  ];

  const agentMap: Record<string, any> = {};

  for (const agentName of agentNames) {
    let agent = await prisma.agent.findUnique({
      where: { name: agentName },
    });

    if (!agent) {
      // Determine agent type
      const type = agentName.includes('general') ? 'COORDINATOR' : 'EXPERT';

      agent = await prisma.agent.create({
        data: {
          name: agentName,
          type: type,
          role: agentName.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
          expertiseAreas: [],
          primaryResponsibilities: [],
          capabilities: [],
          toolsAvailable: [],
          isActive: true,
        },
      });
      console.log(`✅ Created agent: ${agentName}`);
    }

    agentMap[agentName] = agent;
  }

  console.log('');

  // 4. Import PRDs and create user stories
  let importedCount = 0;
  let skippedCount = 0;

  for (const metadata of prdMetadata) {
    // Check if PRD already exists
    const existing = await prisma.pRD.findFirst({
      where: {
        projectId: project.id,
        featureName: metadata.featureName,
      },
    });

    if (existing) {
      console.log(`⏭️  Skipping (already exists): ${metadata.id}`);
      skippedCount++;
      continue;
    }

    // Read PRD content
    if (!fs.existsSync(metadata.filePath)) {
      console.log(`⚠️  File not found: ${metadata.filePath}`);
      continue;
    }

    const prdContent = fs.readFileSync(metadata.filePath, 'utf-8');

    // Create PRD
    const prd = await prisma.pRD.create({
      data: {
        projectId: project.id,
        featureName: metadata.featureName,
        branchName: `feature/${metadata.id.toLowerCase()}`,
        context: `Phase ${metadata.phase} - Priority ${metadata.priority}`,
        prdContent: prdContent,
        riskLevel: metadata.riskLevel,
        version: 1,
        status: 'DRAFT',
      },
    });

    // Extract acceptance criteria from PRD content
    const acceptanceCriteria: string[] = [];
    const handoffMatch = prdContent.match(/## H - HANDOFF[\s\S]*?###\s*Acceptance Criteria([\s\S]*?)(?=###|$)/);

    if (handoffMatch) {
      const criteriaSection = handoffMatch[1];
      const checkboxes = criteriaSection.match(/- \[ \] (.+)/g);

      if (checkboxes) {
        checkboxes.forEach(checkbox => {
          const criterion = checkbox.replace(/- \[ \] /, '').trim();
          if (criterion) {
            acceptanceCriteria.push(criterion);
          }
        });
      }
    }

    // Fallback acceptance criteria if none found
    if (acceptanceCriteria.length === 0) {
      acceptanceCriteria.push('Implementation is complete');
      acceptanceCriteria.push('All tests pass (100% pass rate)');
      acceptanceCriteria.push('Code follows project conventions');
      acceptanceCriteria.push('Documentation is updated');
      acceptanceCriteria.push('Security scan passes (0 violations)');
    }

    // Create user story for this PRD
    const userStory = await prisma.userStory.create({
      data: {
        id: metadata.id,
        prdId: prd.id,
        type: 'IMPLEMENTATION',
        title: metadata.featureName,
        description: `Implement ${metadata.featureName} as defined in PRD`,
        acceptanceCriteria: acceptanceCriteria,
        assignedAgent: metadata.agent,
        priority: metadata.priority,
        complexity: metadata.estimatedHours <= 8 ? 'LOW' : metadata.estimatedHours <= 12 ? 'MEDIUM' : 'HIGH',
        estimatedHours: metadata.estimatedHours,
        dependencies: [],
        constraints: [
          'Follow R-A-L-P-H template structure',
          'Include concrete test examples (pytest/jest/Playwright)',
          'Provide exact validation commands',
          'Meet WCAG 2.2 AA accessibility standards',
        ],
        validationCommands: [
          'npm run type-check',
          'npm run lint',
          'npm test',
          'grep -r "hardcoded" src/',
        ],
        passes: false,
      },
    });

    console.log(`✅ Imported: ${metadata.id} (${metadata.featureName})`);
    console.log(`   Agent: ${metadata.agent}, Hours: ${metadata.estimatedHours}, Risk: ${metadata.riskLevel}`);
    importedCount++;
  }

  console.log('\n' + '='.repeat(80));
  console.log(`✅ Import complete!`);
  console.log(`   Imported: ${importedCount} PRDs`);
  console.log(`   Skipped:  ${skippedCount} PRDs (already exist)`);
  console.log(`   Total:    ${prdMetadata.length} PRDs`);
  console.log('='.repeat(80));
  console.log('\n📊 Next steps:');
  console.log('   1. View PRDs at: http://localhost:3001/projects');
  console.log('   2. Start Ralph Dashboard: cd /home/dev/Development/ralph-dashboard && npm run dev');
  console.log('   3. Begin PRD execution via Ralph Dashboard UI\n');
}

main()
  .catch((e) => {
    console.error('❌ Import failed:', e);
    process.exit(1);
  })
  .finally(async () => {
    await prisma.$disconnect();
  });
