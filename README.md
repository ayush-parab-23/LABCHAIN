# 🛡️ LABCHAIN — Decentralized Medical Report Integrity Network

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.2-teal.svg)](https://palletsprojects.com/p/flask/)
[![Solidity](https://img.shields.io/badge/Solidity-^0.8.0-363636.svg)](https://soliditylang.org/)
[![Hardhat](https://img.shields.io/badge/Hardhat-EVM%20Local-yellow.svg)](https://hardhat.org/)
[![Design System](https://img.shields.io/badge/Design-Clinical%20Teal-0B5D5E.svg)](#-design-direction--clinical-teal)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**LABCHAIN** is a decentralized, healthcare-native medical report verification platform that anchors patient diagnostic reports to an immutable Ethereum smart contract. By coupling **SHA-256 document fingerprinting** with **smart contract ledger anchoring**, LABCHAIN renders medical reports tamper-evident, version-controlled, and instantly verifiable by hospitals and patients worldwide.

---

## 🌟 Key Capabilities

- **Immutable Ledger Anchoring**: Diagnostic PDF digests (SHA-256) are committed directly to an Ethereum smart contract (`LabChain.sol`) with mined block heights, transaction hashes, and timestamps.
- **Cryptographic Tamper Detection**: If even a single byte or character in a diagnostic report is forged, the verification engine detects a `HASH_MISMATCH` and highlights differing characters side-by-side.
- **Document Lifecycle & Versioning**: Issuing laboratories can supersede outdated reports with newer revisions ($v1 \rightarrow v2$) or revoke erroneous diagnoses; previous states remain transparently tracked in the history ledger.
- **Role-Based Access Control (RBAC)**:
  - 🔬 **Laboratory (`LAB`)**: Issue diagnostic reports, commit on-chain anchors, issue superseding corrections, revoke reports, and review audit trail logs.
  - 🏥 **Hospital (`HOSPITAL`)**: Point-of-care verification portal supporting three verification modes (Report ID lookup, drag-and-drop PDF upload, and QR scan).
  - 🧑‍💼 **Patient (`PATIENT`)**: Personal medical vault to inspect certified reports, review version depth, download official PDFs, and open verification QR codes.
  - 🔗 **Blockchain Explorer**: Monospace ledger tables inspecting blocks, transactions, gas consumption, contract addresses, and live search filtering.
- **Minimal Public QR Verification**: Anyone scanning a report's QR code is directed to a clean, minimal verification certificate with all navigation headers hidden.

---

## 🎨 Design Direction: "Clinical Teal"

The user interface follows a healthcare-native **Clinical Teal** design direction engineered to feel calm, trustworthy, and precise:
- **No AI-generated artifacts**: Zero gradients, no glassmorphism, no artificial glows, no purple accents, no emoji icons, and no heavy drop shadows.
- **Micro-details**: 1px hairline borders (`--border`), 8px control radius, 12px card radius, generous whitespace, dense ledger tables, and tabular numbers (`tabular-nums`).
- **Typography**: Google Fonts **IBM Plex Sans** (400, 500) for UI body and **IBM Plex Mono** (400, 500) for report IDs, hashes, blocks, and timestamps. Sentence case across all views.
- **Zero-FOUC Theme Switcher**: Toggle between **Light** (`#F2F7F6`) and **Dark** (`#0C1516`) with an accessible top navigation sun/moon control. An inline `<head>` script prevents any wrong-theme flash, and Chart.js instances dynamically adapt to CSS variables.

---

## 🏗️ System Architecture

```text
LABCHAIN/
├── app.py                      # Flask Application entry point & factory
├── config.py                   # Central configuration & environment loader
├── seed.py                     # Database initialization and default roles/patients
├── make_pdfs.py                # Generates high-fidelity authentic & tampered PDFs
├── register_reports.py         # Hashes and anchors reports to blockchain & SQLite
├── requirements.txt            # Python dependencies
├── .env.example                # Template for environment configuration
├── .gitignore                  # Git ignore rules for Python, Hardhat & SQLite
│
├── blockchain/                 # Hardhat EVM environment
│   ├── contracts/LabChain.sol  # Solidity smart contract
│   ├── scripts/deploy.js       # Deployment script (compiles & writes contract_info.json)
│   ├── hardhat.config.js       # Local EVM consensus node configuration
│   ├── contract_info.json      # Deployed address & ABI (auto-generated)
│   └── blockchain_service.py   # Web3.py wrapper for contract transactions
│
├── database/                   # SQLite database models
│   ├── database.py             # SQLAlchemy instance & login manager
│   └── models.py               # User, Patient, Report, ReportVersion, AuditLog
│
├── routes/                     # Blueprint controllers
│   ├── auth.py                 # Authentication & RBAC decorators
│   ├── lab.py                  # Laboratory issuance & report management
│   ├── patient.py              # Patient vault & secure downloads
│   ├── hospital.py             # Hospital verification portal & public QR endpoints
│   ├── blockchain.py           # Blockchain block & transaction explorer
│   └── analytics.py            # Diagnostic analytics API
│
├── services/                   # Core business logic
│   ├── hashing.py              # SHA-256 calculation
│   ├── verification.py         # Multi-layer DB & on-chain verification
│   ├── qr_service.py           # Base64 QR code generation
│   └── audit_service.py        # Centralized audit logging
│
├── static/                     # CSS tokens, stylesheets, and client scripts
│   ├── css/tokens.css          # Design tokens (colors, radii, typography)
│   ├── css/style.css           # Global typography, layout, tables, buttons
│   ├── css/dashboard.css       # KPI tiles, certificate stamps, timelines
│   └── js/                     # main.js (theme toggle), verification.js, dashboard.js
│
├── templates/                  # Jinja2 HTML templates
│   ├── _components.html        # Reusable macros (KPI tile, status pill, hash chip, diff)
│   ├── base.html               # Master layout with slim top nav & zero-FOUC theme script
│   ├── login.html              # Centered clinical sign-in card
│   ├── lab/                    # Laboratory dashboard, issuance, reports, audit logs
│   ├── patient/                # Patient vault & report detail
│   ├── hospital/               # Hospital verification portal & certificate panels
│   └── blockchain/             # Explorer, block detail, and transaction receipts
│
├── downloads/                  # Sample authentic and tampered PDFs for testing
└── uploads/                    # Server report file store (.gitkeep tracked)
```

---

## ⚡ Prerequisites

- **Python 3.10+**
- **Node.js 18+ & npm** (Required for the Hardhat local Ethereum blockchain)
- **Git**

---

## 🚀 Step-by-Step Setup & Quick Run

### 1. Clone & Set Up the Repository

```bash
git clone https://github.com/<YOUR_USERNAME>/LABCHAIN.git
cd LABCHAIN
```

### 2. Configure Environment Variables

Copy the sample environment file:

```bash
cp .env.example .env
```

*(On Windows PowerShell: `Copy-Item .env.example .env`)*

---

### 3. Terminal 1: Start the Local Hardhat Ethereum Node

Navigate into `blockchain/` and start the consensus node:

```powershell
cd blockchain
npm install
npx.cmd hardhat node
```

> 💡 **Windows Tip**: Use `npx.cmd` instead of `npx` to prevent PowerShell script execution policy restrictions.
> Leave this terminal running. It listens on `http://127.0.0.1:8545`.

---

### 4. Terminal 2: Deploy the Smart Contract

In a new terminal window:

```powershell
cd blockchain
npx.cmd hardhat run scripts/deploy.js --network localhost
```

This compiles `LabChain.sol`, deploys it to the local node, and saves the address and ABI to `blockchain/contract_info.json`.

---

### 5. Terminal 3: Set Up Python Environment & Run the Web App

In a third terminal window from the project root (`LABCHAIN`):

#### A. Create and Activate Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
*(On macOS/Linux: `source venv/bin/activate`)*

#### B. Install Python Dependencies
```powershell
pip install -r requirements.txt
```

#### C. Seed Database Roles and Patients
```powershell
python seed.py
```

#### D. Generate Authentic & Tampered Sample Reports
```powershell
python make_pdfs.py
```

#### E. Anchor Reports to the Blockchain
```powershell
python register_reports.py
```

#### F. Launch Flask Server
```powershell
python app.py
```

Open your browser and navigate to: **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 🔑 Pre-Seeded Demo Accounts

All demo accounts use password: `password123`

| Role | Email | Password | Access Portal |
| :--- | :--- | :--- | :--- |
| **Laboratory (LAB)** | `lab@example.com` | `password123` | [Lab Console](http://127.0.0.1:5000/lab/dashboard) |
| **Hospital (HOSPITAL)** | `hospital@example.com` | `password123` | [Verify Portal](http://127.0.0.1:5000/hospital/dashboard) |
| **Patient (PATIENT)** | `patient@example.com` | `password123` | [Patient Vault](http://127.0.0.1:5000/patient/dashboard) |

---

## 🧪 Hands-On Testing: Authentic vs Tampered Verification

The platform includes a built-in verification test kit on the Hospital Dashboard:

1. Log in to [http://127.0.0.1:5000/login](http://127.0.0.1:5000/login) as **Hospital** (`hospital@example.com` / `password123`).
2. Go to the **Verify Portal** (`/hospital/dashboard`).
3. Notice the **Sample test reports & tampering controls** card:
   - 🟢 **Authentic Report**: Download `Ayush_report.pdf` (Report ID: `LAB-2026-0001`). Upload it to the drag-and-drop zone.
     - **Result**: `AUTHENTIC DOCUMENT VERIFIED` (Green status stamp).
   - 🔴 **Tampered Report**: Download `Ayush_temp.pdf` (where Cholesterol was altered from 185 to 385 mg/dL). Upload it with Report ID `LAB-2026-0001`.
     - **Result**: `TAMPER DETECTED / HASH MISMATCH` (Red status stamp).
     - **Hash Analysis**: Differing characters in the SHA-256 fingerprint are highlighted in red mark elements.

---

## 🔬 Running Automated Tests

Run the test suite to verify database models, hash computation, and smart contract verification logic:

```powershell
python -m unittest discover tests
```

---

## 📤 How to Push This Project to GitHub

Follow these steps to initialize git and push to your personal GitHub account:

```bash
# 1. Initialize git
git init
git branch -M main

# 2. Stage all clean project files (.gitignore excludes venv, node_modules, and .db)
git add .

# 3. Create the initial commit
git commit -m "feat: Initial commit of LABCHAIN Medical Report Integrity Network"

# 4. Link your remote GitHub repository
git remote add origin https://github.com/<YOUR_GITHUB_USERNAME>/<YOUR_REPOSITORY_NAME>.git

# 5. Push to GitHub
git push -u origin main
```

---

## 📜 Smart Contract Reference (`LabChain.sol`)

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract LabChain {
    enum ReportStatus { ACTIVE, SUPERSEDED, REVOKED }

    struct ReportRecord {
        string reportHash;
        string labId;
        uint256 timestamp;
        uint256 version;
        ReportStatus status;
        bool exists;
    }

    // Mapping: reportId => (version => ReportRecord)
    mapping(string => mapping(uint256 => ReportRecord)) public reports;
    mapping(string => uint256) public latestVersions;

    event ReportRegistered(string indexed reportId, uint256 version, string reportHash, string labId);
    event ReportSuperseded(string indexed reportId, uint256 oldVersion, uint256 newVersion, string newHash);
    event ReportRevoked(string indexed reportId, uint256 version);
}
```

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
