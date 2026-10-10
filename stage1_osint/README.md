# Stage 1: The Careers Page Slip-Up (OSINT / Reconnaissance)

- **Module**: IE3132 - Penetration Testing
- **Project**: CyberVault: Operation ShadowTrace
- **Component**: Challenge Design A (Stage 1 of 6)
- **Author**: Member 2 (IT24102386 - Jayakody Y.B.J)
- **Domain**: Open Source Intelligence (OSINT) / Reconnaissance
- **Difficulty**: Easy
- **Service Port**: `8081`

---

## 1. Challenge Overview & Scenario

CyberVault Technologies has published an updated recruitment portal and an employee social activity feed. Before interacting with any hardened endpoints, participants act as junior penetration testers performing passive information gathering. 

An employee accidentally posted details regarding upcoming migration testing, referencing an active internal staging hostname alongside a retired legacy node. The objective is to identify the active internal staging hostname without active port scanning or intrusion tools.

### Learning Objectives
- **LO1**: Apply passive information gathering techniques in the penetration testing process.
- **LO2**: Distinguish between active attack-surface indicators and decommissioned decoy infrastructure.
- **LO3**: Develop automated OSINT harvesting scripts (`solve_stage1.py`).

---

## 2. Technical Build & Architecture

- **Server (`app.py`)**: WSGI Flask application with fallback support, production-ready for both local runs and Vercel serverless execution.
- **Serverless Entrypoint (`api/index.py` & `vercel.json`)**: Configured with path normalization middleware for direct Vercel serverless deployment.
- **Container (`Dockerfile`)**: Lightweight `python:3.11-alpine` container listening on port `8081`.
- **Endpoints**:
  - `GET /` & `GET /careers`: Interactive Careers & Opportunities portal.
  - `GET /social`: Internal company social network stream.
  - `GET /robots.txt`: Search crawler exclusions revealing internal path naming conventions.
  - `GET /api/status`: Health check endpoint.
  - `POST /api/verify`: Validates submitted hostnames and issues the Stage 1 flag.
- **Deployment Guide**: See [`VERCEL_DEPLOYMENT_GUIDE.md`](VERCEL_DEPLOYMENT_GUIDE.md) for full Vercel setup instructions.

---

## 3. Solution Walkthrough

### Intended Path (Manual):
1. Navigate to `http://localhost:8081/careers`.
2. Inspect the engineering positions and the footer domain format (`*.cybervaulttech.com`).
3. Click on the **Employee Feed** (`/social`).
4. Read the posts by the DevOps Engineer and Infrastructure Team:
   - Notice the post referencing the decommissioning of `vault-legacy-01`.
   - Identify the active migration destination: `vault-staging.cybervaulttech.com`.
5. Enter `vault-staging.cybervaulttech.com` into the validation form on the page.
6. The validation endpoint returns the Stage 1 flag and directs the tester to Stage 2 (`http://localhost:8082`).

### Automated Path (LO3 Solver):
Run the automated reconnaissance solver:
```bash
python solve_stage1.py
```
Or via the local batch runner:
```bat
..\python.bat solve_stage1.py
```

---

## 4. Flag Placement & Details

- **Flag**: `CVT{0s1nt_st4g1ng_l34k_8291}`
- **Decoy Identified**: `vault-legacy-01` (retired infrastructure)
- **Correct Hostname**: `vault-staging.cybervaulttech.com`
- **Next Target**: `http://localhost:8082` (Stage 2 - Steganography)

---

## 5. Progressive Hints
- **Hint 1 (Free)**: Two hostnames are mentioned across the pages. One is explicitly retired and decommissioned.
- **Hint 2 (Targeted)**: The decommissioned host is `vault-legacy-01`. Find the active migration host on the `.cybervaulttech.com` domain.

---

## 6. Reset & Recovery
- **Stateless Container**: The service maintains no persistent state; restarting the container or application immediately restores it to a pristine state.
- **Docker Command**: `docker restart cybervault_stage1_osint`
