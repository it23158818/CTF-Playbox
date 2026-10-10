# Vercel Deployment Guide for Stage 6: System Security & Linux Privilege Escalation Capstone

The `stage6_capstone_host` challenge provides an interactive Bash terminal web console simulating the SSH service account on the staging host. It is fully configured and optimized for zero-configuration serverless deployment on [Vercel](https://vercel.com/) as a Python WSGI web application.

---

## 1. Project Structure for Vercel

```text
stage6_capstone_host/
├── api/
│   └── index.py             # Serverless entrypoint exposing WSGI app with VercelPathMiddleware
├── templates/
│   └── terminal.html        # Interactive cybersecurity web terminal interface
├── vercel.json              # Vercel URL rewrite routing configuration
├── .vercelignore            # Excludes Dockerfile, VM scripts, virtualenvs, and test tools
├── requirements.txt         # Production dependencies for Vercel Python runtime (Flask>=2.2.0)
├── capstone_server.py       # Core terminal simulation engine and API endpoints
├── app.py                   # Local WSGI application entrypoint
├── solve_stage6.py          # Automated privilege escalation verifier script
├── Dockerfile               # Container deployment configuration for offline / local VM labs
└── README.md                # Stage overview and solution documentation
```

---

## 2. Deployment Options

### Option A: Deploying via Vercel Web Dashboard (GitHub Integration)

1. Push your branch (`IT24103027`) to **GitHub**.
2. Log in to [vercel.com](https://vercel.com/) and click **"Add New" ➔ "Project"**.
3. Select your repository: `it23158818/CTF-Playbox`.
4. Under **"Root Directory"**, click **Edit** and set:
   ```text
   stage6_capstone_host
   ```
   *(Or `Asignmet 2/stage6_capstone_host` depending on your repository root)*.
5. In **"Build and Output Settings"**, leave default settings (Framework Preset: **Other**).
6. *(Optional)* In **"Environment Variables"**, configure any custom variables (see Section 3 below).
7. Click **Deploy**. Vercel will automatically package the Python WSGI serverless function and launch the terminal challenge!

---

### Option B: Deploying via Vercel CLI

1. Open a terminal and navigate to `stage6_capstone_host`:
   ```bash
   cd stage6_capstone_host
   ```
2. Install the Vercel CLI (if not already installed):
   ```bash
   npm i -g vercel
   ```
3. Deploy to preview:
   ```bash
   vercel
   ```
4. Deploy directly to production:
   ```bash
   vercel --prod
   ```

---

## 3. Environment Variables (Optional)

Configure these variables in your **Vercel Project Settings ➔ Environment Variables** if you wish to customize flag values:

| Variable Name | Description | Default Value |
| :--- | :--- | :--- |
| `STAGE6_FLAG` | The CTF root flag awarded upon successful sudo privilege escalation | `CVT{r00t_pr1v_3sc_c4pst0n3_mast3r}` |
| `PORT` | Local runtime port (used when running `python app.py` or `python capstone_server.py`) | `5006` |

---

## 4. API Endpoints

Once deployed on Vercel, the application exposes:

- `GET /` — Renders the interactive terminal web console.
- `POST /api/exec` — Executes terminal commands (`whoami`, `id`, `uname -a`, `sudo -l`, `sudo /usr/local/bin/backup-vault.sh`, etc.) and returns JSON results.
- `GET /health` — Health check endpoint returning JSON service status.
- `POST /reset` — Resets the simulated environment.

---

## 5. Testing Your Deployed Vercel Instance

Once deployed, you can verify your Vercel instance using the automated solver script:

```bash
python solve_stage6.py https://<your-project>.vercel.app
```

The script will automatically perform:
1. Low-privilege enumeration (`whoami`, `id`, `uname -a`)
2. Permission verification test (`cat /root/flag.txt` -> Permission Denied)
3. Sudoers audit (`sudo -l` -> identifies `NOPASSWD: /usr/local/bin/backup-vault.sh`)
4. Elevated privilege execution (`sudo /usr/local/bin/backup-vault.sh`)
5. Captures and verifies the Root Flag: `CVT{r00t_pr1v_3sc_c4pst0n3_mast3r}`.
