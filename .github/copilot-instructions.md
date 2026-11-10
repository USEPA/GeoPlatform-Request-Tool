# Working in this repository

Trust these instructions first; search only when information is missing, contradicted by the checkout, or demonstrably incorrect.

## Purpose and architecture

The EPA Account Request Tool provisions GeoPlatform/GeoSecure ArcGIS accounts and group access for emergency responses/projects. Sponsors (Team Coordinators) and Delegates review requests; administrators configure portals/responses. Preserve their permissions and distinguish creating accounts from enabling existing accounts.

Small monorepo (~234 tracked files): Python 3.11/Django 4.2/DRF backend; Angular 15/Material/RxJS/TypeScript 4.8.4 frontend; SQLite default, PostgreSQL 14 in Compose, Windows IIS deployments. No root npm project.

| Location | Responsibility |
| --- | --- |
| `manage.py`, `AGOLAccountRequestor/settings.py`, `urls.py` | Django entry point, environment configuration, API router; `/api/v1/`, `/api/current_user/`, `/api/admin/`, `/api/oauth2/`. `URL_PREFIX` changes deployment paths. |
| `AGOLAccountRequestor/agol_auth.py`, `views.py` | ArcGIS OAuth pipeline, current user, redirects, coordinator emails. |
| `accounts/models.py`, `func.py` | Portal HTTP integration, account/response models, notifications; approval, role/user-type updates, username formatting, group membership. Model saves have side effects. |
| `accounts/views.py`, `serializers.py`, `permissions.py`, `validators.py`, `admin.py` | DRF endpoints/validation/access control and Django admin. |
| `accounts/migrations/`, `tests.py`, `fixtures/fixtures.json` | Schema through 0037; Django tests/mock portal requests/fixtures. Root `oauth2_migrations/` is legacy, not configured as an override. |
| `accounts/management/commands/` | Portal credential setup/refresh and notification jobs; these can modify external systems/send email, so do not run as smoke tests. |
| `templates/`, `accounts/templates/`, `_static/`, `core/mixins.py` | Admin/email templates, admin assets, shared content-type list behavior. |
| `ui/src/main.ts`, `app/app.module.ts`, `app/app-routing.module.ts` | Angular bootstrap/module/routes; feature directories contain components, templates, CSS, colocated Jasmine specs. |
| `ui/src/app/auth/`, `services/base.service.ts`, `types.ts`, `dialogs/`, `core/material.module.ts` | Login/route guards/user config, shared paginated HTTP service, API types, request/approval dialogs, Material imports. |
| `ui/angular.json`, `src/environments/`, `proxy.conf.json` | Build configurations, deployment endpoints, development `/api` proxy to `127.0.0.1:8000`. |

Root files: `README.md` (purpose), `requirements.txt`, `.gitignore`, `Dockerfile.{api,web}`, `docker-compose{,.dev,.innovate}.yml`, `Jenkinsfile`. Guides: `ui/src/assets/AcctRequestUserGuide.pdf`, `_static/GPOAcctRequestAdminGuide.pdf`. `ui/README.md` has obsolete Angular 7/Protractor guidance; prefer package scripts.

## Bootstrap and backend validation

Use a clean disposable checkout without deployment `.env`/databases. Settings call `load_dotenv()`; `DATABASES` is JSON, otherwise SQLite applies. Unit tests need no PostgreSQL/OAuth credentials. Never include secrets/dumps in Docker contexts: `Dockerfile.api` copies everything; no `.dockerignore` exists.

Validated through **Ubuntu WSL inside Docker**, using `python:3.11`. On Windows invoke Docker through `wsl -d Ubuntu`, not host Python/npm; never reuse an existing database. Following Bash commands run inside these containers or equivalent cloud Ubuntu environments. Versions exercised: Python 3.11.18, Django 4.2.30.

From the repository root, always install dependencies before checks:

```bash
python -m venv /tmp/request-tool-venv
source /tmp/request-tool-venv/bin/activate
python -m pip install -r requirements.txt
python -m pip check
python manage.py check
python manage.py test --noinput
python manage.py makemigrations --check --dry-run
```

**Dependency pitfall:** without the `social-auth-core` 5.1.x requirement, 6.2.0 caused `ImportError: MissingBackend` with `social-auth-app-django==5.0.0` (~3 seconds). The current constraint resolved to 5.1.1 and restored all 39 tests; preserve it. `pip check` alone misses this incompatibility.

Tests manage their own SQLite database/fixtures; no prior migrations required. Target with `python manage.py test accounts.tests.TestAccounts`. For disposable development:

```bash
python manage.py migrate --noinput
python manage.py collectstatic --noinput
DEBUG=True ALLOWED_HOSTS=localhost,127.0.0.1 python manage.py runserver 0.0.0.0:8000 --noreload
```

Admin login returned HTTP 200; tests passed before/after migrations/static collection. Parent directory must be writable (`../error.log`). Baseline warnings: AutoField defaults, ManyToMany `null`; mocked tests print `Error creating test.user at geoplatform.` despite success. Add migrations for model changes.

## Frontend validation and running

Always install from the lockfile before tests/builds:

```bash
cd ui
export NODE_OPTIONS=--max_old_space_size=4096
npm ci
npm run test:ci
npm run build:ngst-staging
npm run build:ngst-prod
```

Karma requires Chrome/Chromium via `CHROME_BIN`. Missing browser/Cypress libraries in the Debian Node container required:

```bash
apt-get update -qq
apt-get install -y --no-install-recommends chromium libgtk-3-0 libgbm1 libasound2 xvfb xauth
export CHROME_BIN=/usr/bin/chromium
```

Only when testing as root in a disposable container, Chromium additionally requires a launcher wrapper:

```bash
printf '#!/bin/sh\nexec /usr/bin/chromium --no-sandbox "$@"\n' > /tmp/request-chrome
chmod +x /tmp/request-chrome
export CHROME_BIN=/tmp/request-chrome
```

Use LF shell scripts; CRLF causes "not found". All 26 frontend tests passed despite existing NG0303 template logs; a temporary added spec (27 total) and rebuild also passed.

`npm start -- --host 0.0.0.0` serves port 4200 (HTTP 200 verified); adjust the API proxy for separate containers. `npm test` watches; targeted: `npm run test:ci -- --include='src/app/approval-list/*.spec.ts'`. All four builds (`build:prod`, `build:staging`, `build:ngst-staging`, `build:ngst-prod`) passed, producing `ui/dist/ui`. Existing warnings: Material themes, unused TS files, nested CSS. Install ~43s; builds ~23-38s; backend tests ~3s; frontend tests ~10-22s. No timeouts occurred.

`npm run lint` fails: no lint target/ESLint config. Legacy `ui/{,src/}tslint.json` is inactive; `.editorconfig` specifies two spaces. Compiler/tests: `ui/tsconfig.json`, `src/tsconfig.{app,spec}.json`, `src/karma.conf.js`, `src/test.ts`. No backend lint or precommit hook is tracked.

## E2E and CI constraints

`npx cypress verify` passed. Scripts: `cypress:run`/`e2e` run Cypress; `cypress:open` is interactive. Active config/specs: `ui/cypress.config.ts`, `ui/cypress/e2e/`; `ui/e2e/` is legacy. E2E requires a reachable app/API, seeded responses/groups/roles ("R09 Testing"), `approver_username`/`approver_password` in untracked `ui/cypress.env.json`, and test-only Django settings `DRF_RECAPTCHA_TESTING = True`, `DRF_RECAPTCHA_TESTING_PASS = True` on the actual backend (not read from environment). Set `CYPRESS_BASE_URL`. Full E2E remains unverified without these prerequisites; unreachable-server verification failed after ~13s. Tests mutate data: never target production or disable production reCAPTCHA.

PRs to `master`: `.github/workflows/test_and_deploy_staging.yml` builds `Dockerfile.api`, runs backend tests, then Node 20 `npm ci`, `test:ci`, `build:ngst-staging`; self-hosted Windows deployment runs migrate/collectstatic then Cypress with secrets. Pushes to `master`: `deploy_production.yml` builds `build:ngst-prod` and deploys IIS. `issue_tracking.yml` manages issues only. `Jenkinsfile` is a separate Windows staging/E2E/approval flow. Never execute deployment steps locally.

`Dockerfile.api` built (~51s, includes collectstatic); preserve the auth constraint for runtime checks. `Dockerfile.web` is stale: nonexistent `npm run build` (verified failure), absent `template.nginx`, obsolete outputs/private image. Innovate Compose calls undeclared `gunicorn`; unit tests need no Compose. Before submitting, repeat relevant tests/builds/migration checks and inspect the diff; exclude generated static/build files, credentials, databases.
