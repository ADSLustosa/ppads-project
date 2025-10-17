import { test, expect } from '@playwright/test';
import { LoginPage } from './pom/LoginPage';

test.beforeEach(async ({ request }) => {
  await request.post(`${process.env.API_URL}/test/reset`);
  await request.post(`${process.env.API_URL}/test/seed`, { data:{
    user:{ email:process.env.USER_EMAIL, senha:process.env.USER_PASS },
    contas:[{ saldo:1000 }],
    chavesPix:[{ tipo:'email', valor:process.env.DEST_PIX }]
  }});
});

test('TC029 Pix válido', async ({ page }) => {
  const login = new LoginPage(page);
  await login.goto();
  await login.login(process.env.USER_EMAIL!, process.env.USER_PASS!);
  await page.getByTestId('menu-pix').click();
  await page.getByTestId('pix-chave').fill(process.env.DEST_PIX!);
  await page.getByTestId('pix-valor').fill('50');
  await page.getByTestId('pix-enviar').click();
  await expect(page.getByText(/Pix enviado com sucesso/i)).toBeVisible();
  await page.getByTestId('menu-extrato').click();
  await expect(page.getByText(/DEBITO.*PIX.*50,00/i)).toBeVisible();
});

test('TC031 Pix saldo insuficiente', async ({ page }) => {
  const login = new LoginPage(page);
  await login.goto();
  await login.login(process.env.USER_EMAIL!, process.env.USER_PASS!);
  await page.getByTestId('menu-pix').click();
  await page.getByTestId('pix-chave').fill(process.env.DEST_PIX!);
  await page.getByTestId('pix-valor').fill('5000');
  await page.getByTestId('pix-enviar').click();
  await expect(page.getByText(/Saldo insuficiente/i)).toBeVisible();
});