import { Page } from '@playwright/test';
export class LoginPage {
  constructor(private page: Page) {}
  async goto(){ await this.page.goto('/'); }
  async login(email: string, pass: string){
    await this.page.getByTestId('email').fill(email);
    await this.page.getByTestId('senha').fill(pass);
    await this.page.getByTestId('entrar').click();
  }
}