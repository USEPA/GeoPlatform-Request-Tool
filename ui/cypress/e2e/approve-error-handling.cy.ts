import '../support/commands';

/**
 * E2E tests for approval error-handling around update_user_type_and_role.
 *
 * A dedicated account request is created in `before`, edited into an
 * approveable state (matching the pattern used in specs.cy.ts), and
 * deleted in `after`.  Each test then intercepts the approve endpoint to
 * exercise every response shape the backend can return without touching
 * the real AGOL portal.
 */

const TEST = {
  first_name: 'ErrorTest',
  last_name:  'Handle',
  email:      'errortest.handle@epa.gov',
  organization: 'Test Org',
  response:   'R09 Testing',
  /** format_username output: last.capitalize() + '.' + first.capitalize() + '_EPA' */
  username:   'Handle.Errortest_EPA',
};

const APPROVE_ENDPOINT = '**/v1/account/approvals/approve/';
const SNACKBAR = 'span[class="mat-simple-snack-bar-content"]';

// ─── helpers ──────────────────────────────────────────────────────────────────

/** Open the edit dialog for the test record and add a group so it becomes approveable. */
function editRecordToApproveableState() {
  cy.visit('/accounts/list');
  cy.get('input#searchInput').type(`${TEST.first_name} ${TEST.last_name}{enter}`);
  cy.wait(1000);
  cy.get('mat-cell').first().click();
  cy.get('button#editBtn').click();
  // wait for groups dropdown to become enabled (response must be selected first)
  cy.wait(1000);
  cy.get('mat-select[formcontrolname="groups"].mat-select-disabled', {timeout: 30000}).should('not.exist');
  cy.get('mat-select[formcontrolname="groups"]').click();
  cy.get('.mat-option-text').contains('Test').click();
  cy.get('body').click();
  cy.wait(1000); // submit button is briefly disabled
  cy.get('button').contains('Submit').click();
  cy.get(SNACKBAR).should('contain', 'Success');
}

/** Navigate to the list, search for the test record, and select its row. */
function selectTestRecord() {
  cy.visit('/accounts/list');
  cy.get('input#searchInput').type(`${TEST.first_name} ${TEST.last_name}{enter}`);
  cy.wait(1000);
  cy.get('mat-cell').first().click();
}

/**
 * Click through the GeoPlat two-dialog approval flow.
 *
 * 1. ChooseCreationMethodComponent  → click "Send Email Invitation(s)" / "Confirm Approval"
 * 2. GenericConfirmDialogComponent  → click "Confirm"
 *
 * At this point the intercepted POST to /approve/ fires and the test can
 * assert the resulting snackbar.
 */
function triggerApproveFlow() {
  cy.get('button#approveBtn').click();
  // First dialog: choose creation method (GeoPlat)
  cy.get('button').contains(/Send Email Invitation|Confirm Approval/).click();
  // Second dialog: generic confirmation
  cy.get('button').contains('Confirm').click();
}

// ─── suite ────────────────────────────────────────────────────────────────────

describe('Approve – update_user_type_and_role error handling', () => {

  // ── one-time setup: create + make approveable ──────────────────────────────
  before(() => {
    // 1. Submit an account request anonymously (same pattern as specs.cy.ts)
    cy.visit('/');
    cy.get('input[formcontrolname="first_name"]').type(TEST.first_name);
    cy.get('input[formcontrolname="last_name"]').type(TEST.last_name);
    cy.get('input[formcontrolname="email"]').type(TEST.email);
    cy.get('input[formcontrolname="organization"]').type(TEST.organization);
    cy.get('mat-select[formcontrolname="response"]').click();
    cy.get('mat-option', {timeout: 30000}).contains(TEST.response).click();
    cy.get('button').contains('Submit').click();
    cy.get(SNACKBAR, {timeout: 30000}).should('contain', 'Request has been successfully submitted');

    // 2. Log in as approver and edit the record to satisfy approval requirements
    cy.loginWithCredentials(Cypress.env('approver_username'), Cypress.env('approver_password'));
    editRecordToApproveableState();
  });

  // ── one-time teardown: delete the record ──────────────────────────────────
  after(() => {
    cy.loginWithCredentials(Cypress.env('approver_username'), Cypress.env('approver_password'));
    cy.visit('/accounts/list');
    cy.get('input#searchInput').type(`${TEST.first_name} ${TEST.last_name}{enter}`);
    cy.wait(1000);
    cy.get('mat-cell').first().click();
    cy.get('mat-cell.cdk-column-delete > button').click();
    cy.get('button').contains('Confirm').click();
    cy.get(SNACKBAR).should('contain', `Deleted ${TEST.username}`);
  });

  // ── per-test login ─────────────────────────────────────────────────────────
  beforeEach(() => {
    cy.loginWithCredentials(Cypress.env('approver_username'), Cypress.env('approver_password'));
  });

  // ── tests ──────────────────────────────────────────────────────────────────

  // 1. User-type update failure (500 + structured JSON body)
  it('shows the backend error message when user type update fails', () => {
    cy.intercept('POST', APPROVE_ENDPOINT, {
      statusCode: 500,
      body: {
        id: 1,
        error: `Failed to update user type for ${TEST.username} at GeoPlatform.`
      }
    }).as('approveUserTypeError');

    selectTestRecord();
    triggerApproveFlow();

    cy.wait('@approveUserTypeError');
    cy.get(SNACKBAR, {timeout: 10000}).should('contain', 'Failed to update user type');
  });

  // 2. Role update failure (500 + structured JSON body)
  it('shows the backend error message when user role update fails', () => {
    cy.intercept('POST', APPROVE_ENDPOINT, {
      statusCode: 500,
      body: {
        id: 1,
        error: `Failed to update user role for ${TEST.username} at GeoPlatform.`
      }
    }).as('approveRoleError');

    selectTestRecord();
    triggerApproveFlow();

    cy.wait('@approveRoleError');
    cy.get(SNACKBAR, {timeout: 10000}).should('contain', 'Failed to update user role');
  });

  // 3. Generic 500 without a structured body (unhandled server exception)
  it('shows an error snackbar on a generic 500 response', () => {
    cy.intercept('POST', APPROVE_ENDPOINT, {
      statusCode: 500,
      body: 'Internal Server Error'
    }).as('approveGenericError');

    selectTestRecord();
    triggerApproveFlow();

    cy.wait('@approveGenericError');
    cy.get('.snackbar-error', {timeout: 10000}).should('exist');
  });

  // 4. Permission denied (403) – e.g. username/email mismatch
  it('shows the detail message on a 403 permission denied response', () => {
    cy.intercept('POST', APPROVE_ENDPOINT, {
      statusCode: 403,
      body: {
        detail: 'Provided email address is not associated with this existing username.'
      }
    }).as('approvePermissionDenied');

    selectTestRecord();
    triggerApproveFlow();

    cy.wait('@approvePermissionDenied');
    cy.get(SNACKBAR, {timeout: 10000})
      .should('contain', 'not associated with this existing username');
  });

  // 5. Partial success – account processed but groups not added (200 + warning)
  it('shows a warning snackbar when groups could not be added', () => {
    cy.intercept('POST', APPROVE_ENDPOINT, {
      statusCode: 200,
      body: {
        id: 1,
        warning: `Warning, ${TEST.username} created but groups not added at GeoPlatform.`
      }
    }).as('approveGroupWarning');

    selectTestRecord();
    triggerApproveFlow();

    cy.wait('@approveGroupWarning');
    cy.get(SNACKBAR, {timeout: 10000}).should('contain', 'issue adding to groups');
    cy.get('.snackbar-warning', {timeout: 10000}).should('exist');
  });

  // 6. Full success (200 + success) – regression / control case
  it('shows a success snackbar when approval completes without errors', () => {
    cy.intercept('POST', APPROVE_ENDPOINT, {
      statusCode: 200,
      body: {
        id: 1,
        success: `Successfully approved ${TEST.username} at GeoPlatform.`
      }
    }).as('approveSuccess');

    selectTestRecord();
    triggerApproveFlow();

    cy.wait('@approveSuccess');
    cy.get(SNACKBAR, {timeout: 10000}).should('contain', 'Success');
    cy.get('.snackbar-success', {timeout: 10000}).should('exist');
  });

});
