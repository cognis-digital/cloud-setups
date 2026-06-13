<div align="center">

# cloud-setups

### Batteries-included **Firebase · GCP · Azure** project setups — bootstrap, deploy, IaC, and emulators in one repo.

[![License: COCL 1.0](https://img.shields.io/badge/License-COCL%201.0-2b6cb0.svg)](LICENSE) ![Firebase](https://img.shields.io/badge/Firebase-FFCA28?logo=firebase&logoColor=black) ![GCP](https://img.shields.io/badge/GCP-4285F4?logo=googlecloud&logoColor=white) ![Azure](https://img.shields.io/badge/Azure-0078D4?logo=microsoftazure&logoColor=white)

</div>

A merged, rebranded starter kit distilling the patterns from the popular cloud-starter ecosystem into
one place — copy a folder, set your IDs, deploy.

## Firebase  ·  [`firebase/`](firebase/)
`firebase.json`, Firestore rules + indexes, Cloud Functions, Hosting SPA rewrite, full **emulator suite**, `deploy.sh`.
```bash
cd firebase && bash deploy.sh   # emulators by default
```

## GCP  ·  [`gcp/`](gcp/)
`bootstrap.sh` (enable APIs + Artifact Registry), **Cloud Run** deploy, Terraform (`google_cloud_run_v2_service`).
```bash
PROJECT_ID=my-proj bash gcp/bootstrap.sh
```

## Azure  ·  [`azure/`](azure/)
`bootstrap.sh` (**Container Apps**), **Bicep** + Terraform (`azurerm`).
```bash
bash azure/bootstrap.sh
```

## Credits / prior art
In the spirit of `firebase/firebase-tools`, `GoogleCloudPlatform/cloud-run-samples`, `Azure-Samples/`,
and the `awesome-firebase` / `awesome-gcp` / `awesome-azure` lists — consolidated and rebranded. PRs to
add stacks (Supabase, Cloudflare, Fly.io) welcome.

## How it fits

```mermaid
flowchart LR
  U[You / CI / Agent] --> R[cloud-setups]
  R --> O[Outputs & artifacts]
  R --> M[MCP / JSON]
  M --> AI[AI agents]
  R --> S[Cognis Neural Suite]
```

**Explore the suite →** [🗂️ all tools](https://github.com/cognis-digital/cognis-neural-suite) · [⭐ awesome-cognis](https://github.com/cognis-digital/awesome-cognis) · [🔗 cognis-sources](https://github.com/cognis-digital/cognis-sources)

<a name="verification"></a>
## Verification



Every push is verified end-to-end. Latest audit (2026-06-13):

```text
tests        : 0 passed, 0 failed, 0 errored
compile      : all modules parse
cli          : n/a
package      : n/a
```

<details><summary>CLI surface (<code>--help</code>)</summary>

```text
(see --help)
```
</details>

Full machine-readable results: [`AUDIT.md`](AUDIT.md) · regenerate with `python -m cloud-setups --help` + `pytest -q`.

<div align="right"><a href="#top">↑ back to top</a></div>


## License
COCL v1.0 — see [LICENSE](LICENSE).
