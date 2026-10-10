# Vercel Deployment Guide for Stage 1: The Careers Page Slip-Up (OSINT)

The `stage1_osint` challenge is fully configured and optimized for zero-configuration or custom serverless deployment on [Vercel](https://vercel.com/) as a Python serverless web application.

---

## 1. Project Structure for Vercel

```text
stage1_osint/
├── api/
│   └── index.py             # Serverless entrypoint exposing WSGI app with VercelPathMiddleware
├── vercel.json              # Vercel URL rewrite routing configuration
├── .vercelignore            # Excludes Dockerfile, solvers, virtualenvs, and temporary files
├── requirements.txt         # Production dependencies for Vercel Python runtime (Flask>=2.2.0)
├── app.py                   # Core application serving OSINT careers portal, feed, and verification API
├── Dockerfile               # Container deployment configuration
├── solve_stage1.py          # Automated reconnaissance solver script
└── README.md                # Stage overview and solution documentation
```

---

## 2. Deployment Options

### Option A: Deploying via Vercel Web Dashboard (GitHub Integration)

1. Push your repository to **GitHub** (or GitLab/Bitbucket).
2. Log in to [vercel.com](https://vercel.com/) and click **"Add New" ➔ "Project"**.
3. Select your repository.
4. Under **"Root Directory"**, click **Edit** and select:
   ```text
   stage1_osint
   ```
5. *(Optional)* In **"Environment Variables"**, configure any custom variables (see Section 3 below).
6. Click **Deploy**. Vercel will build the Python serverless function and launch the challenge!

---

### Option B: Deploying via Vercel CLI

1. Open a terminal and change directory to `stage1_osint`:
   ```bash
   cd stage1_osint
   ```
2. Install the Vercel CLI (if not already installed):
   ```bash
   npm i -g vercel
   ```
3. Deploy to preview:
   ```bash
   vercel
   ```
4. Deploy to production:
   ```bash
   vercel --prod
   ```

---

## 3. Environment Variables (Optional)

Configure these variables in your **Vercel Project Settings ➔ Environment Variables** if you wish to override defaults:

| Variable Name | Description | Default Value |
| :--- | :--- | :--- |
| `STAGE1_FLAG` | The CTF flag awarded upon identifying the active staging host | `CVT{0s1nt_st4g1ng_l34k_8291}` |
| `STAGE2_URL` | The next stage handoff URL displayed after solving | `http://localhost:8082` |
| `PORT` | Local runtime port (used when running `python app.py` locally) | `8081` |

---

## 4. Testing Your Deployed Vercel Instance

Once deployed, you can verify your Vercel instance using the automated reconnaissance solver script by passing your deployment URL:

```bash
python solve_stage1.py https://<your-project>.vercel.app
```

The solver will:
1. Ping `https://<your-project>.vercel.app/api/status`
2. Fetch and parse `/careers` and `/social`
3. Identify the active host `vault-staging.cybervaulttech.com` while skipping `vault-legacy-01`
4. Submit the hostname to `https://<your-project>.vercel.app/api/verify`
5. Print the verified security flag.
