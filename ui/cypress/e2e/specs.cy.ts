import '../support/commands';

describe('Anonymous submission', () => {
  beforeEach(() => {
    cy.visit('/')
  })
  it('anyone can submit account request', () => {

    cy.get('input[formcontrolname="first_name"]').type('Test')
    cy.get('input[formcontrolname="last_name"]').type('User')
    cy.get('input[formcontrolname="email"]').type('notanemail')
    cy.get('input[formcontrolname="organization"]').type('some org')

    cy.get('mat-error').first().should('contain', 'Not a valid email')

    cy.get('input[formcontrolname="email"]').type('@epa.gov')
    cy.get('mat-select[formcontrolname="response"]').click();
    cy.get('mat-option', {timeout: 30000}).contains('R09 Testing').click();
    // cy.solveGoogleReCAPTCHA();

    cy.get('button').contains('Submit').click();
    cy.get('span[class="mat-simple-snack-bar-content"]', {timeout: 30000}).should('contain', 'Request has been successfully submitted')
  })

  it('block submitting same request ', () => {
    cy.get('input[formcontrolname="first_name"]').type('Test')
    cy.get('input[formcontrolname="last_name"]').type('User')
    cy.get('input[formcontrolname="email"]').type('notanemail@epa.gov')
    cy.get('input[formcontrolname="organization"]').type('some org')
    cy.get('mat-select[formcontrolname="response"]').click();
    cy.get('mat-option').contains('R09 Testing').click();
    // cy.solveGoogleReCAPTCHA();
    cy.get('button').contains('Submit').click();
    cy.get('span[class="mat-simple-snack-bar-content"]').should('contain', 'Outstanding request found.')
  })

  it('should go to login if trying to submit response form', () => {
    cy.get('button').contains('Configure New Response / Project').click();
    cy.url().should('contain', '/login');
  })

  it('should not allow requests if not in approve domain list for enterprise', () => {
    cy.get('input[formcontrolname="first_name"]').type('Test')
    cy.get('input[formcontrolname="last_name"]').type('User')
    cy.get('input[formcontrolname="email"]').type('notanemail')
    cy.get('input[formcontrolname="organization"]').type('some org')

    cy.get('mat-error').first().should('contain', 'Not a valid email')

    cy.get('input[formcontrolname="email"]').type('@whoknows.gov')
    cy.get('mat-select[formcontrolname="response"]').click();
    cy.get('mat-option', {timeout: 30000}).contains('Geosecure test').click();
    // cy.solveGoogleReCAPTCHA();

    cy.get('button').contains('Submit').click();
    cy.get('span[class="mat-simple-snack-bar-content"]', {timeout: 30000}).should('contain', 'Request can not be accepted at this time.')

  })

  it('should preselect response/project if response in query params', () => {
    cy.visit('/?response=1');
    cy.get('mat-select[formcontrolname="response"]').should('contain', 'R09 Testing')
  })

  it('should not filter responses if response in query params does not exist', () => {
    cy.visit('/?response=999999')
    cy.get('mat-select[formcontrolname="response"]').click();
    cy.get('mat-option', {timeout: 30000}).should('exist')
  })
})


describe('approver workflow', () => {
  beforeEach(() => {
    cy.loginWithCredentials(Cypress.env('approver_username'), Cypress.env('approver_password'));
    cy.visit('/');
  })

  it('should allow logged in user to submit response form', () => {
    cy.get('button').contains('Configure New Response / Project').click();
    cy.get('input[formcontrolname="name"]').type('Test')
    cy.get('mat-select[formcontrolname="default_reason"]').click();
    cy.get('mat-option').contains('Emergency Response').click();
    cy.get('app-tag-input').type('test');
    cy.get('mat-option').first().click();
    cy.get('mat-select[formcontrolname="authoritative_group"]').click();
    cy.get('mat-option').first().click();
    cy.get('mat-dialog-content button').contains('Submit').scrollIntoView().click();
    cy.get('span[class="mat-simple-snack-bar-content"]').should('contain', 'Request has been successfully submitted');
  })

  it('should allow approver to go to approval list', () => {
    cy.get('button#userName').click();
    cy.get('button').contains('Approval List').click();
    cy.url().should('contain', '/accounts/list');
  })

  it('should allow user to toggle filter', () => {
    cy.visit('/accounts/list');
    cy.get('mat-sidenav').should('be.hidden');
    cy.get('button#filterBtn').click();
    cy.get('button#filterBtn').should('contain', 'Hide Filter');
    cy.get('mat-sidenav').should('be.visible');
  })

  it('should allow user to search for requests', () => {
    cy.visit('/accounts/list');
    cy.get('input#searchInput').type('Test User{enter}')
    cy.get('.cdk-cell.cdk-column-first_name').first().should('contain', 'Test')
    cy.get('.cdk-cell.cdk-column-last_name').first().should('contain', 'User')
  })

  it('should not allow approver to immediate approve', () => {
    cy.visit('/accounts/list');
    cy.get('input#searchInput').type('Test User{enter}')
    cy.wait(1000);
    cy.get('mat-cell').first().click();
    cy.get('button#editBtn').should('be.visible')
    cy.get('button#approveBtn').should('not.exist')
  })


  it('should allow approver to edit request', () => {
    cy.visit('/accounts/list');
    cy.get('input#searchInput').type('Test User{enter}')
    cy.wait(1000);
    cy.get('mat-cell').first().click();
    cy.get('button#editBtn').click()
    cy.wait(1000);
    cy.get('mat-select[formcontrolname="groups"].mat-select-disabled').should('not.exist')
    cy.get('mat-select[formcontrolname="groups"]').click();
    cy.get('.mat-option-text').contains('Test').click();
    cy.get('body').click()
    cy.wait(1000) // submit button is greyed out for a moment
    cy.get('button').contains('Submit').click();
    cy.get('span[class="mat-simple-snack-bar-content"]').should('contain', 'Success');
  })

  it('should allow approver to approve request', () => {
    cy.visit('/accounts/list');
    cy.get('input#searchInput').type('Test User{enter}')
    cy.wait(1000);
    cy.get('mat-cell').first().click();
    cy.get('button#approveBtn').click()
    cy.get('.mat-dialog-content').should('exist')
  })

  it('should allow apporver to delete the request', () => {
    cy.visit('/accounts/list');
    cy.get('input#searchInput').type('Test User{enter}')
    cy.wait(1000);
    cy.get('mat-cell').first().click();
    cy.get('mat-cell.cdk-column-delete > button').click()
    cy.get('button').contains('Confirm').click();
    cy.get('span[class="mat-simple-snack-bar-content"]').should('contain', 'Deleted User.Test_EPA')

  })

})
