import { useState } from "react";
import type { FormEvent } from "react";
import "./Login.css";

type LoginProps = {
  onSignedIn: () => void;
};

export default function Login({ onSignedIn }: LoginProps) {
  const [registering, setRegistering] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  function switchMode() {
    setRegistering((current) => !current);
    setPassword("");
    setShowPassword(false);
    setError("");
    setNotice("");
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (loading) return;

    setError("");
    setNotice("");

    if (registering && password.length < 12) {
      setError("Choose a password of at least 12 characters.");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(
        registering ? "/api/auth/register" : "/api/auth/login",
        {
          method: "POST",
          credentials: "same-origin",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email: email.trim(),
            password,
          }),
        }
      );

      const data = await response.json().catch(() => null);

      if (!response.ok) {
        if (response.status === 422) {
          throw new Error(
            "Enter a valid email address. New passwords must contain 12–128 characters."
          );
        }

        if (response.status === 401) {
          throw new Error("Email or password is incorrect.");
        }

        if (response.status === 409) {
          throw new Error(
            "Unable to create this account. Try signing in instead."
          );
        }

        if (response.status === 403) {
          throw new Error(
            "Open this application at http://localhost:5173 and try again."
          );
        }

        if (response.status === 404) {
          throw new Error(
            "The account service was not found. Check that the updated backend is running."
          );
        }

        throw new Error(
          "The account service is unavailable. Please try again."
        );
      }

      if (
        !registering &&
        (!data || typeof data.email !== "string")
      ) {
        throw new Error(
          "The account service returned an unexpected response."
        );
      }

      setPassword("");
      setShowPassword(false);

      if (registering) {
        setRegistering(false);
        setNotice("Account created. Enter your password to sign in.");
      } else {
        onSignedIn();
      }
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to connect. Please try again."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="account-page">
      <section className="account-story">
        <a href="/" className="account-brand">
          <span className="account-symbol" aria-hidden="true">P</span>
          People’s Guide
        </a>

        <div className="account-story-body">
          <p className="account-eyebrow">
            A CLEARER WAY FORWARD
          </p>

          <h1>
            The Right Support.
            <br />
            The Right Information.
            <br />
            <span>One Place.</span>
          </h1>

          <p className="account-description">
            Describe your situation in your own words.
            Explore relevant public services and practical next
            steps, with links to official guidance.
          </p>

          <ul className="account-features">
            <li>
              <strong>Local AI processing</strong>
              <span>
                Powered by our team’s NVIDIA DGX Spark.
              </span>
            </li>
            <li>
              <strong>Official reference sources</strong>
              <span>
                See the public guidance retrieved for your response.
              </span>
            </li>
            <li>
              <strong>Practical next steps</strong>
              <span>
                Understand your options and where to go next.
              </span>
            </li>
          </ul>
        </div>

        <p className="account-story-footer">
          Built around people.
        </p>
      </section>

      <section className="account-access">
        <div className="account-card">
          <span className="account-pill">
            YOUR PEOPLE’S GUIDE ACCOUNT
          </span>

          <h2>
            {registering ? "Create your account." : "Welcome back."}
          </h2>

          <p className="account-subtitle">
            {registering
              ? "One account. A clearer place to start."
              : "Sign in to continue to your support navigator."}
          </p>

          <form onSubmit={handleSubmit}>
            <label htmlFor="account-email">
              Email address
            </label>

            <input
              id="account-email"
              name="email"
              type="email"
              autoComplete="username"
              placeholder="you@example.com"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              maxLength={254}
              disabled={loading}
              required
            />

            <label htmlFor="account-password">
              Password
            </label>

            <div className="account-password">
              <input
                id="account-password"
                name="password"
                type={showPassword ? "text" : "password"}
                autoComplete={
                  registering ? "new-password" : "current-password"
                }
                placeholder={
                  registering
                    ? "At least 12 characters"
                    : "Enter your password"
                }
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                minLength={registering ? 12 : 1}
                maxLength={128}
                aria-describedby={
                  registering ? "account-password-help" : undefined
                }
                disabled={loading}
                required
              />

              <button
                type="button"
                className="account-show"
                onClick={() => setShowPassword((current) => !current)}
                aria-label={
                  showPassword ? "Hide password" : "Show password"
                }
                aria-pressed={showPassword}
                disabled={loading}
              >
                {showPassword ? "Hide" : "Show"}
              </button>
            </div>

            {registering && (
              <p id="account-password-help" className="account-help">
                Use a unique password of 12–128 characters.
              </p>
            )}

            {error && (
              <p className="account-error" role="alert">
                {error}
              </p>
            )}

            {notice && (
              <p className="account-notice" role="status">
                {notice}
              </p>
            )}

            <button
              type="submit"
              className="account-submit"
              disabled={loading}
            >
              <span>
                {loading
                  ? "Please wait…"
                  : registering
                    ? "Create account"
                    : "Sign in"}
              </span>
              <span aria-hidden="true">→</span>
            </button>
          </form>

          <button
            type="button"
            className="account-switch"
            onClick={switchMode}
            disabled={loading}
          >
            {registering
              ? "Already have an account? Sign in"
              : "New here? Create an account"}
          </button>

          <p className="account-prototype">
            Hackathon prototype. Email verification and password
            recovery are not available yet.
          </p>
        </div>

        <footer className="account-access-footer">
          Guidance to help you explore services.
          Official services determine eligibility.
        </footer>
      </section>
    </main>
  );
}