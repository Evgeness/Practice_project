import { useState } from 'react'

export function AuthPage({ onLogin, onRegister }) {
  const [mode, setMode] = useState('login')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [passwordConfirmation, setPasswordConfirmation] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const changeMode = (nextMode) => {
    setMode(nextMode)
    setPassword('')
    setPasswordConfirmation('')
    setError('')
  }

  const submit = async (event) => {
    event.preventDefault()
    setError('')

    const cleanUsername = username.trim()
    if (mode === 'register') {
      if (cleanUsername.length < 3) {
        setError('Логин должен содержать минимум 3 символа')
        return
      }
      if (password.length < 8) {
        setError('Пароль должен содержать минимум 8 символов')
        return
      }
      if (password !== passwordConfirmation) {
        setError('Пароли не совпадают')
        return
      }
    }

    setLoading(true)
    try {
      if (mode === 'register') {
        await onRegister(cleanUsername, password)
      } else {
        await onLogin(cleanUsername, password)
      }
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : mode === 'register'
            ? 'Ошибка регистрации'
            : 'Ошибка авторизации',
      )
    } finally {
      setLoading(false)
    }
  }

  const isRegister = mode === 'register'
  const isSubmitDisabled =
    loading ||
    !username.trim() ||
    !password ||
    (isRegister && !passwordConfirmation)

  return (
    <main className="login-page">
      <section className="login-card" aria-labelledby="auth-title">
        <p className="eyebrow">База знаний университета</p>

        <div className="auth-tabs" role="tablist" aria-label="Авторизация">
          <button
            type="button"
            role="tab"
            aria-selected={!isRegister}
            className={!isRegister ? 'active' : ''}
            onClick={() => changeMode('login')}
          >
            Вход
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={isRegister}
            className={isRegister ? 'active' : ''}
            onClick={() => changeMode('register')}
          >
            Регистрация
          </button>
        </div>

        <h1 id="auth-title">{isRegister ? 'Создание аккаунта' : 'Вход в систему'}</h1>
        <p className="login-card__description">
          {isRegister
            ? 'Придумайте логин и пароль. После регистрации вы сразу войдёте в систему.'
            : 'Введите данные зарегистрированного пользователя.'}
        </p>

        <form className="login-form" onSubmit={submit}>
          <label>
            <span>Логин</span>
            <input
              name="username"
              autoComplete="username"
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              minLength={isRegister ? 3 : 1}
              maxLength={50}
              required
              autoFocus
            />
          </label>
          <label>
            <span>Пароль</span>
            <input
              name="password"
              type="password"
              autoComplete={isRegister ? 'new-password' : 'current-password'}
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              minLength={isRegister ? 8 : 1}
              maxLength={200}
              required
            />
          </label>

          {isRegister && (
            <label>
              <span>Повторите пароль</span>
              <input
                name="passwordConfirmation"
                type="password"
                autoComplete="new-password"
                value={passwordConfirmation}
                onChange={(event) => setPasswordConfirmation(event.target.value)}
                minLength={8}
                maxLength={200}
                required
              />
            </label>
          )}

          {isRegister && (
            <p className="password-hint">
              Минимум 8 символов. Логин может содержать буквы, цифры, точку, дефис и
              подчёркивание.
            </p>
          )}

          {error && <p className="error-banner">{error}</p>}
          <button type="submit" disabled={isSubmitDisabled}>
            {loading
              ? isRegister
                ? 'Регистрируем...'
                : 'Входим...'
              : isRegister
                ? 'Зарегистрироваться'
                : 'Войти'}
          </button>
        </form>
      </section>
    </main>
  )
}
