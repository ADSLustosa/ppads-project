import { test, expect } from '@playwright/test';
import { LoginPage } from './pom/LoginPage';

test('TC009 Login válido', async ({ page }) => {
  const login = new LoginPage(page);
  await login.goto();
  await login.login(process.env.USER_EMAIL!, process.env.USER_PASS!);
  await expect(page.getByText(/Dashboard/i)).toBeVisible();
});

test('TC011 Login inválido', async ({ page }) => {
  const login = new LoginPage(page);
  await login.goto();
  await login.login('x@x.com','Errada@123');
  await expect(page.getByText(/E-mail ou senha incorretos/i)).toBeVisible();
});