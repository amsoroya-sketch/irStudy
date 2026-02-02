# irStudy Tauri Desktop Application Architecture

**Version**: 1.0.0
**Date**: 2026-02-02
**Status**: Design Phase (Implementation starts Week 2)
**Owner**: Developer 4 (AI/ML + Tauri Lead)

---

## 1. Executive Summary

The irStudy Tauri desktop application provides an offline-first medical education platform for ICRP exam preparation. This architecture document defines the technical design, security requirements, and implementation roadmap for Week 2+ development.

### Key Requirements
- **Offline Support**: Full functionality without internet connectivity
- **Exam Lockdown**: Secure testing environment with browser/app restrictions
- **Data Sync**: Bidirectional sync with cloud backend when online
- **Cross-Platform**: Windows, macOS, Linux support
- **Bundle Size**: Target 3-5MB (compressed), <20MB (installed)
- **Security**: Encrypted local storage, zero PHI leaks, audit logging

---

## 2. Technology Stack

### 2.1 Core Technologies

| Component | Technology | Version | Rationale |
|-----------|-----------|---------|-----------|
| **Desktop Framework** | Tauri | 1.5+ | Rust security, 3MB bundle, 20-40x smaller than Electron |
| **Backend Runtime** | Rust | 1.70+ | Memory safety, FFI performance, cryptographic libraries |
| **Frontend Framework** | React 18 | 18.2+ | Existing codebase compatibility, TypeScript support |
| **Build Tool** | Vite | 5.0+ | Fast HMR, optimized production builds |
| **Local Database** | SQLCipher | 4.5+ | Encrypted SQLite with AES-256-CBC |
| **State Management** | Zustand | 4.4+ | Lightweight (1KB), TypeScript-first, simpler than Redux |
| **UI Library** | Material-UI | 5.14+ | Consistent with web app, WCAG 2.1 AA compliant |
| **HTTP Client** | Reqwest (Rust) | 0.11+ | Async HTTP with TLS 1.3 support |
| **Sync Protocol** | CRDTs | custom | Conflict-free replicated data types for offline sync |

### 2.2 Development Tools

- **Package Manager**: npm/pnpm (frontend), Cargo (Rust backend)
- **Linting**: ESLint (TypeScript), Clippy (Rust)
- **Testing**: Vitest (unit), Playwright (E2E), cargo test (Rust)
- **CI/CD**: GitHub Actions (automated builds for Windows/macOS/Linux)

---

## 3. Architecture Overview

### 3.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Tauri Desktop App                        │
├─────────────────────────────────────────────────────────────┤
│  Frontend (React)                                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ MCQ Viewer │ OSCE Trainer │ Progress Dashboard       │   │
│  │ Study Cards│ Analytics    │ Settings                 │   │
│  └──────────────────────────────────────────────────────┘   │
│                         ↕ (IPC via Tauri Commands)           │
│  Backend (Rust)                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Sync Manager │ Auth Manager │ Lockdown Controller    │   │
│  │ Data Manager │ Crypto       │ Audit Logger           │   │
│  └──────────────────────────────────────────────────────┘   │
│                         ↕                                    │
│  Local Storage (SQLCipher)                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ mcqs.db (encrypted) │ user_data.db │ sync_state.db   │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                          ↕ (HTTPS when online)
┌─────────────────────────────────────────────────────────────┐
│              Cloud Backend (FastAPI)                         │
│  PostgreSQL │ Redis │ Qdrant │ Neo4j                        │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Tauri IPC Architecture

Tauri uses a secure Inter-Process Communication (IPC) model where the frontend (WebView) communicates with the Rust backend via commands:

```rust
// Rust backend command
#[tauri::command]
async fn get_mcqs(
    state: tauri::State<'_, AppState>,
    limit: u32,
    offset: u32
) -> Result<Vec<MCQ>, String> {
    // Fetch from SQLCipher database
    let db = state.db.lock().await;
    db.query_mcqs(limit, offset).await
}

// Frontend invocation
import { invoke } from '@tauri-apps/api/tauri';

const mcqs = await invoke('get_mcqs', { limit: 10, offset: 0 });
```

**Security Benefits**:
- No Node.js runtime (eliminates 1000+ CVEs from Electron)
- Rust memory safety prevents buffer overflows
- IPC permissions controlled via `tauri.conf.json`
- CSP (Content Security Policy) enforced on WebView

---

## 4. Data Architecture

### 4.1 Local Database Schema (SQLCipher)

**Database**: `irStudy.db` (AES-256-CBC encrypted)

**Tables**:

```sql
-- User profile (single row)
CREATE TABLE user (
    id TEXT PRIMARY KEY,
    email TEXT NOT NULL UNIQUE,
    full_name TEXT NOT NULL,
    role TEXT CHECK(role IN ('student', 'educator', 'admin')),
    created_at INTEGER NOT NULL,
    synced_at INTEGER
);

-- MCQ content (downloaded from cloud)
CREATE TABLE mcqs (
    id TEXT PRIMARY KEY,
    specialty TEXT NOT NULL, -- 'cardiology', 'respiratory', 'psychiatry'
    difficulty TEXT NOT NULL, -- 'easy', 'medium', 'hard'
    question TEXT NOT NULL,
    options TEXT NOT NULL, -- JSON array
    correct_answer TEXT NOT NULL,
    explanation TEXT NOT NULL,
    citations TEXT NOT NULL, -- JSON array
    image_url TEXT,
    tags TEXT, -- JSON array
    created_at INTEGER NOT NULL,
    synced_at INTEGER
);

-- User MCQ attempts (offline first)
CREATE TABLE mcq_attempts (
    id TEXT PRIMARY KEY,
    mcq_id TEXT NOT NULL REFERENCES mcqs(id),
    user_id TEXT NOT NULL REFERENCES user(id),
    selected_answer TEXT NOT NULL,
    is_correct INTEGER NOT NULL CHECK(is_correct IN (0, 1)),
    time_spent_seconds INTEGER NOT NULL,
    attempted_at INTEGER NOT NULL,
    synced INTEGER DEFAULT 0 CHECK(synced IN (0, 1))
);

-- OSCE content
CREATE TABLE osces (
    id TEXT PRIMARY KEY,
    specialty TEXT NOT NULL,
    scenario TEXT NOT NULL,
    marking_rubric TEXT NOT NULL, -- JSON
    time_limit_minutes INTEGER NOT NULL,
    created_at INTEGER NOT NULL,
    synced_at INTEGER
);

-- Sync state (CRDT vector clocks)
CREATE TABLE sync_state (
    entity_type TEXT PRIMARY KEY, -- 'mcq_attempts', 'user_progress'
    last_synced_at INTEGER NOT NULL,
    vector_clock TEXT NOT NULL -- JSON: {'server': 42, 'device_abc': 10}
);

-- Indexes for performance
CREATE INDEX idx_mcqs_specialty ON mcqs(specialty);
CREATE INDEX idx_mcqs_difficulty ON mcqs(difficulty);
CREATE INDEX idx_mcq_attempts_user ON mcq_attempts(user_id);
CREATE INDEX idx_mcq_attempts_synced ON mcq_attempts(synced);
```

### 4.2 Encryption Key Management

**Challenge**: SQLCipher requires a passphrase to encrypt/decrypt the database.

**Solution**: Derive encryption key from user password + device ID using Argon2id:

```rust
use argon2::{Argon2, PasswordHasher};
use rand::Rng;

fn derive_db_key(user_password: &str, device_id: &str) -> Result<String, Error> {
    let salt = format!("{}-irstudy-salt", device_id);
    let argon2 = Argon2::default();

    let password_hash = argon2.hash_password(
        user_password.as_bytes(),
        &salt
    )?;

    Ok(password_hash.to_string())
}
```

**Security Properties**:
- Key never stored on disk (derived on-demand)
- User must be authenticated to access database
- Device ID prevents cross-device key reuse
- Argon2id protects against rainbow table attacks

---

## 5. Offline Sync Protocol

### 5.1 CRDT-Based Sync Strategy

**Problem**: User attempts MCQs offline on Device A, then online on Device B. How do we merge conflicting attempts without data loss?

**Solution**: Use **Conflict-Free Replicated Data Types (CRDTs)** with vector clocks.

**Vector Clock Example**:
```json
{
  "server": 42,
  "device_abc123": 10,
  "device_xyz789": 5
}
```

### 5.2 Sync Algorithm (Rust Implementation)

```rust
async fn sync_mcq_attempts(
    local_db: &SqlCipherConnection,
    remote_api: &ApiClient,
    user_id: &str
) -> Result<SyncReport, Error> {
    // 1. Get local vector clock
    let local_clock = local_db.get_vector_clock("mcq_attempts").await?;

    // 2. Pull changes from server (send local clock to minimize data transfer)
    let remote_changes = remote_api.get_mcq_attempts_since(user_id, &local_clock).await?;

    // 3. Apply remote changes to local database
    for attempt in remote_changes {
        // CRDT merge: if attempt.id exists locally, compare timestamps
        if let Some(local_attempt) = local_db.get_attempt(&attempt.id).await? {
            if attempt.updated_at > local_attempt.updated_at {
                // Remote is newer, overwrite local
                local_db.upsert_attempt(&attempt).await?;
            }
            // Else: local is newer, skip (will be pushed later)
        } else {
            // New attempt from server, insert
            local_db.insert_attempt(&attempt).await?;
        }
    }

    // 4. Push local unsynced changes to server
    let local_unsynced = local_db.get_unsynced_attempts().await?;
    for attempt in local_unsynced {
        remote_api.upload_mcq_attempt(&attempt).await?;
        local_db.mark_as_synced(&attempt.id).await?;
    }

    // 5. Update local vector clock
    local_db.update_vector_clock("mcq_attempts", &remote_clock).await?;

    Ok(SyncReport {
        pulled: remote_changes.len(),
        pushed: local_unsynced.len(),
    })
}
```

### 5.3 Conflict Resolution Rules

| Conflict Type | Resolution Strategy |
|---------------|---------------------|
| **Same MCQ attempted twice** | Keep both attempts (user may retry) |
| **User profile updated on 2 devices** | Last-write-wins (based on `updated_at`) |
| **Progress stats mismatch** | Server recomputes from all attempts |

---

## 6. Exam Lockdown Features

### 6.1 Security Requirements

For secure exam mode (Week 3 feature):

1. **Disable Browser Access**: Block all browsers using system-level hooks
2. **Screenshot Detection**: Detect and block screenshot tools (Windows Snipping Tool, macOS Shift+Cmd+4)
3. **Process Monitoring**: Terminate blacklisted apps (Discord, Slack, VS Code)
4. **Webcam Monitoring**: Optional proctoring (requires user consent, HIPAA compliant)
5. **Audit Logging**: Log all exam events (start, pause, submit, violations)

### 6.2 Rust Implementation (Lockdown Controller)

```rust
#[cfg(target_os = "windows")]
fn enable_lockdown_mode() -> Result<(), Error> {
    use winapi::um::winuser::{BlockInput, SetWindowsHookExW};

    // 1. Block Alt+Tab, Alt+F4
    unsafe {
        BlockInput(TRUE);
    }

    // 2. Monitor active window titles
    let blacklist = vec!["Chrome", "Firefox", "Discord", "Slack"];
    for process in system.processes() {
        if blacklist.contains(&process.name()) {
            process.kill()?;
        }
    }

    // 3. Set exam mode flag (audit log)
    audit_log("exam_lockdown_enabled", &[("timestamp", Utc::now().to_rfc3339())]);

    Ok(())
}
```

**Limitations**:
- macOS System Integrity Protection (SIP) prevents some hooks
- Linux has no standard API (must use X11/Wayland hooks)
- Requires admin/root privileges on first launch

**Recommendation**: Implement as **opt-in** for high-stakes practice exams, not enforced by default.

---

## 7. Security Architecture

### 7.1 Threat Model

| Threat | Mitigation |
|--------|-----------|
| **Data theft from stolen device** | SQLCipher AES-256 encryption, no key on disk |
| **Memory dumping attacks** | Rust memory safety, zeroize sensitive data after use |
| **Network MITM attacks** | TLS 1.3 only, certificate pinning |
| **Code injection via XSS** | CSP headers, React DOM escaping |
| **Tampering with local database** | HMAC signatures on synced data |

### 7.2 HIPAA Compliance

**PHI Handling**:
- No patient data stored (only de-identified exam content)
- User email considered PHI → encrypted at rest
- Audit logs retain 7 years (HIPAA requirement)
- No PHI in error logs or crash reports

**Encryption Standards**:
- At-rest: AES-256-CBC (SQLCipher)
- In-transit: TLS 1.3 with AEAD ciphers
- Key derivation: Argon2id (OWASP recommended)

---

## 8. Bundle Size Optimization

**Target**: 3-5MB compressed, <20MB installed

### 8.1 Size Breakdown (Estimated)

| Component | Size | Optimization |
|-----------|------|--------------|
| Tauri core | 2.5 MB | Static linking, strip debug symbols |
| WebView2 (Windows) | 0 MB | Uses system WebView2 |
| WebKit (macOS) | 0 MB | Uses system WebKit |
| Rust binaries | 1.5 MB | `--release` build, LTO enabled |
| React bundle | 0.8 MB | Vite code splitting, tree shaking |
| Material-UI | 0.5 MB | Import only used components |
| SQLCipher | 0.4 MB | Statically linked |
| **Total** | **5.7 MB** | |

### 8.2 Optimization Techniques

**Cargo.toml** (Rust):
```toml
[profile.release]
opt-level = "z"        # Optimize for size
lto = true             # Link-time optimization
codegen-units = 1      # Single codegen unit (slower build, smaller binary)
strip = true           # Strip debug symbols
```

**Vite config** (Frontend):
```typescript
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          'vendor': ['react', 'react-dom'],
          'mui': ['@mui/material']
        }
      }
    },
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true // Remove console.logs in production
      }
    }
  }
});
```

---

## 9. Implementation Roadmap

### Week 2 (Tauri MVP)
- [ ] Initialize Tauri project: `npm create tauri-app`
- [ ] Setup SQLCipher integration (Rust crate)
- [ ] Implement basic IPC commands (get_mcqs, submit_answer)
- [ ] Create offline-first data layer
- [ ] Port MCQ viewer component from web app
- [ ] Implement sync manager (pull-only for now)
- [ ] Bundle for Windows/macOS/Linux
- [ ] Test bundle size (<10MB)

### Week 3 (Sync + Lockdown)
- [ ] Implement CRDT sync algorithm
- [ ] Add conflict resolution logic
- [ ] Create exam lockdown mode (opt-in)
- [ ] Add process monitoring
- [ ] Implement audit logging
- [ ] Test offline → online → offline workflow

### Week 4 (Polish + Deploy)
- [ ] Add auto-update mechanism (Tauri updater)
- [ ] Create Windows installer (MSI)
- [ ] Create macOS DMG with code signing
- [ ] Create Linux AppImage
- [ ] CI/CD pipeline for automated releases
- [ ] Security audit (penetration testing)

---

## 10. Alternative Architectures Considered

### 10.1 Electron (Rejected)

**Pros**: Large ecosystem, mature tooling
**Cons**:
- 150MB+ bundle size (30x larger than Tauri)
- Node.js runtime security vulnerabilities
- Higher memory usage (2x Tauri)

**Decision**: Rejected due to bundle size and security concerns.

### 10.2 Progressive Web App (PWA) (Rejected)

**Pros**: No installation, cross-platform
**Cons**:
- Limited offline support (Service Worker limitations)
- No exam lockdown features (browser sandboxing)
- Can't access SQLCipher (Web SQL deprecated)

**Decision**: Rejected due to offline and security requirements. May implement as complementary option.

### 10.3 React Native (Rejected)

**Pros**: Mobile support, large ecosystem
**Cons**:
- No desktop support (Electron bridge needed)
- JavaScript security risks
- Large bundle size

**Decision**: Rejected due to desktop focus. May revisit for mobile in future.

---

## 11. Open Questions

1. **Auto-update strategy**: Should updates be mandatory or optional? (Security vs user autonomy)
2. **Proctoring ethics**: Is webcam monitoring ethical for self-study? (Likely NO - remove feature)
3. **Cross-device limits**: Should users be limited to 2-3 devices? (Prevent account sharing)
4. **Offline duration**: Should app require online check-in every 30 days? (License verification)

**Decision Date**: 2026-02-09 (Week 2 kickoff meeting)

---

## 12. References

- [Tauri Documentation](https://tauri.app/v1/guides/)
- [SQLCipher Encryption](https://www.zetetic.net/sqlcipher/)
- [CRDT Sync Algorithms](https://crdt.tech/)
- [OWASP Mobile Security](https://owasp.org/www-project-mobile-security/)
- [HIPAA Security Rule](https://www.hhs.gov/hipaa/for-professionals/security/index.html)

---

**Document Status**: ✅ Complete
**Next Review**: 2026-02-09 (Week 2 start)
**Approval Required**: Product Manager, Security Lead

---

*Generated with [Claude Code](https://claude.com/claude-code)*
*Co-Authored-By: Claude <noreply@anthropic.com>*
