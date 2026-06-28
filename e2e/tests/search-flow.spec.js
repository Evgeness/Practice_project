import { expect, test } from '@playwright/test'
import path from 'node:path'

const fixture = path.resolve('../backend/tests/fixtures/sample.docx')

const username = process.env.AUTH_USERNAME ?? 'student'
const password = process.env.AUTH_PASSWORD ?? 'practice2026'

test('login -> upload -> indexing -> search -> results', async ({ page }) => {
  await page.goto('/')
  await page.getByLabel('Логин').fill(username)
  await page.getByLabel('Пароль').fill(password)
  await page.getByRole('button', { name: 'Войти' }).click()

  await expect(page.getByText(/Пользователь:/)).toBeVisible()
  await page.locator('input[type=file]').setInputFiles(fixture)
  await expect(page.getByText('Готово', { exact: true })).toBeVisible({ timeout: 90_000 })

  await page.getByLabel('Поисковый запрос').fill('университетская база знаний')
  await page.getByRole('button', { name: 'Найти' }).click()

  await expect(page.getByText(/Найдено фрагментов/)).toBeVisible()
  await expect(page.locator('article.result-card').first()).toBeVisible()
})


test('registration -> automatic login', async ({ page }) => {
  const uniqueUsername = `student_${Date.now()}`
  await page.goto('/')
  await page.getByRole('tab', { name: 'Регистрация' }).click()
  await page.getByLabel('Логин').fill(uniqueUsername)
  await page.getByLabel('Пароль', { exact: true }).fill('registration2026')
  await page.getByLabel('Повторите пароль').fill('registration2026')
  await page.getByRole('button', { name: 'Зарегистрироваться' }).click()

  await expect(page.getByText(`Пользователь: ${uniqueUsername}`)).toBeVisible()
})
