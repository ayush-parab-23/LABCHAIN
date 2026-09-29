# 🚀 LABCHAIN — Quick Run & Command Reference Guide

This single reference file contains every command and step needed to run the entire LABCHAIN system from scratch on Windows.

---

## 📋 Summary of Terminals Needed

Running LABCHAIN requires 2 or 3 terminal windows:
1. **Terminal 1**: Local Hardhat Ethereum Blockchain Node
2. **Terminal 2**: Smart Contract Deployment (run once, then can close)
3. **Terminal 3**: Flask Web Application

---

## ⚡ Quick Copy-Paste Commands

### 🟢 Terminal 1: Start Hardhat Blockchain Node

Open PowerShell and run:

```powershell
cd C:\Users\AYUSH\.gemini\antigravity\scratch\LABCHAIN\blockchain
npx.cmd hardhat node
```

> ⚠️ **Important**: 
> - Use `npx.cmd` on Windows (not `npx`) to avoid PowerShell execution policy errors.
> - **Leave this terminal open!** It runs the blockchain node on `http://127.0.0.1:8545`.

---

### 🟢 Terminal 2: Deploy Smart Contract

Open a new PowerShell terminal and run:

```powershell
cd C:\Users\AYUSH\.gemini\antigravity\scratch\LABCHAIN\blockchain
npx.cmd hardhat run scripts/deploy.js --network localhost
```

> ℹ️ This compiles `LabChain.sol`, deploys it to the local node, and saves the address & ABI to `contract_info.json`. Once it prints `Contract info written to: ...`, you can close this terminal or reuse it.

---

### 🟢 Terminal 3: Database Setup & Run Web App

Open a new PowerShell terminal at the project root (`LABCHAIN`):

#### 1. Activate the Python Virtual Environment
```powershell
cd C:\Users\AYUSH\.gemini\antigravity\scratch\LABCHAIN
.\venv\Scripts\Activate.ps1
```
*(If PowerShell gives a script permission error, run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` or use `.\venv\Scripts\activate.bat`)*

#### 2. Seed Default Database Roles & Patients
```powershell
python seed.py
```

#### 3. Generate Clinical Report PDFs
```powershell
python make_pdfs.py
```

#### 4. Anchor & Register Reports on Blockchain
```powershell
python register_reports.py
```
*(You will see transaction blocks mined live in Terminal 1!)*

#### 5. Start the Flask Web Server
```powershell
python app.py
```

🎉 Open your browser at: **[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 🔑 Login Accounts (Password: `password123` for all)

| Role | Email | Password | What You Can Do |
| :--- | :--- | :--- | :--- |
| **Laboratory** | `lab@example.com` | `password123` | Upload new reports, register on blockchain, correct versions, view analytics |
| **Patient** | `patient@example.com` | `password123` | View Ayush's reports, download authentic PDFs, generate QR code |
| **Hospital** | `hospital@example.com` | `password123` | Verify reports by uploading PDF or entering Report ID, blockchain explorer |

---

## 🧪 Testing Verification & Tamper Detection

1. Log into `http://127.0.0.1:5000` with **`hospital@example.com`** / **`password123`**.
2. Click **Verify Report** on the navigation bar.
3. **Test Genuine Report**:
   - Upload `downloads/Ayush_report.pdf` (or enter Report ID `LAB-2026-0001`).
   - Expected Result: 🟢 **VERIFIED / AUTHENTIC** (SHA-256 matches blockchain record).
4. **Test Tampered Report**:
   - Upload `downloads/Ayush_temp.pdf` (where cholesterol was changed from 185 to 385 mg/dL).
   - Expected Result: 🔴 **TAMPERED / HASH MISMATCH** (Alert triggered immediately).

---

## 🧪 Run Automated Tests

To run the unit test suite at any time:

```powershell
.\venv\Scripts\python.exe -m unittest tests/test_core.py
```

---

## 🛠️ Troubleshooting Common Windows Issues

| Issue | Cause | Fix |
| :--- | :--- | :--- |
| `npm.ps1 cannot be loaded...` | PowerShell Script Execution Policy | Use `npm.cmd` and `npx.cmd` instead of `npm` / `npx`. |
| `Activate.ps1 cannot be loaded...` | Script execution blocked | Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in your terminal. |
| `Unable to connect to local blockchain` | Hardhat node is not running | Ensure Terminal 1 is running `npx.cmd hardhat node`. |
| `Smart contract not loaded` | Contract hasn't been deployed yet | Run `npx.cmd hardhat run scripts/deploy.js --network localhost` in `blockchain/`. |
