import '../support/commands';

describe("reponse admin", () => {
  beforeEach(() => {
    cy.loginWithCredentials(Cypress.env('approver_username'), Cypress.env('approver_password'));

    cy.visit('http://localhost:8000/api/admin/')
  })
  it('changing portal should clear selections', () => {
    cy.visit('http://localhost:8000/api/admin/accounts/responseproject/3/change/')
    cy.get("select[name='requester']").should('contain.value', '3')
    cy.get("select[name='users']").should('contain.value', '3')
    // expect(cy.get("select[name='assignable_groups']").invoke('val')).to.include(3)
    cy.get("select[name='portal']").select('GeoPlatform');
    cy.get("select[name='requester']").should('contain.value', '')
    cy.get("select[name='role']").should('contain.value', '')
    cy.get("select[name='users']").invoke('val').should('deep.equal', [])
    cy.get("select[name='assignable_groups']").invoke('val').should('deep.equal', [])

    cy.get('input').contains('Save and continue editing').click()

    cy.get('.field-requester li').should('contain', 'This field is required.')
    cy.get('.field-users li').should('contain', 'This field is required.')
    cy.get('.field-assignable_groups li').should('contain', 'This field is required.')
    cy.get('.field-role li').should('contain', 'This field is required.')
  })

  it('should only require auth group for certain portal', () => {
    cy.visit('http://localhost:8000/api/admin/accounts/responseproject/3/change/');
    cy.get("select[name='portal']").select('GeoPlatform');
    cy.get('input').contains('Save and continue editing').click();
    cy.get('.field-authoritative_group li').should('contain', 'The Authoritative Group must be available under the selected Role. Check the Role\'s allowed Authoritative Groups.')
    cy.get("select[name='portal']").select('GeoSecure');

    cy.get('input').contains('Save and continue editing').click();
    cy.get('.field-authoritative_group li').should('not.exist');

  })
})
