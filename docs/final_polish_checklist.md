# Final Polish Checklist

## 1) Git Validation

- `git status --short` must be empty.
- `git log --oneline -15` should include recent commits:
  - dashboard + analytics endpoints
  - analytics snapshot docs
  - snapshot pipeline + snapshot mode

## 2) Screenshot Capture

Store all files under:

- `docs/screenshots/`

Required screenshots:

1. `swagger-overview.png`:
   - Swagger groups visible (`flights`, `operations`, `audit`).
2. `ops-delay-summary.png`:
   - Response for `GET /ops/delay-summary`.
3. `ops-snapshot-latest.png`:
   - Response for `GET /ops/metrics-snapshots/latest`.
4. `dashboard-overview.png`:
   - Dashboard landing view (`http://localhost:8501`).
5. `dashboard-snapshot-mode.png`:
   - Dashboard with `Snapshot` mode selected.
6. `dashboard-route-or-airport.png`:
   - Route Analysis or Airport Analysis tab.
7. `docker-compose-ps.png`:
   - `docker compose ps` with `mongo`, `api`, `dashboard` all `Up`.
8. `k8s-resources.png`:
   - `kubectl get all -n aeroops`.
9. `acr-repository.png`:
   - Azure Container Registry showing `aeroops-api:latest`.

## 3) Demo Default

Use `Snapshot` mode as the default demo path in the walkthrough.

## 4) Recruiter Package

- Use `docs/recruiter_pitch.md` as outreach template.
- Use `docs/cv_bullet_aeroops.md` for CV entry.
- Use `docs/demo_script_3_5_min.md` for live demo.
