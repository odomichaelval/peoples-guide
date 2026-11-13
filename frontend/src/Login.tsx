import { useState } from "react";
import type { FormEvent } from "react";
import "./Login.css";

type LoginProps = {
  onSignedIn: () => void;
};

export default function Login({ onSignedIn }: LoginProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [message, setMessage] = useState("");
  const [registering, setRegistering] = useState(false);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (loading) return;

    setLoading(true);
    setMessage("");

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

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : "Please check your email and password."
        );
      }

      setPassword("");

      if (registering) {
        setRegistering(false);
        setMessage("Account created. Enter your password to sign in.");
      } else {
        onSignedIn();
      }
    } catch (error) {
      setMessage(
        error instanceof Error
          ? error.message
          : "Unable to connect. Please try again."
      );
    } finally {
      setLoading(false);
    }
  }

  function switchMode() {
    setRegistering((current) => !current);
    setPassword("");
    setMessage("");
  }

  return (
    <main className="pg-login">
      <section className="pg-story" aria-label="About People's Guide">
        <a className="pg-logo" href="/">
          <span className="pg-mark" aria-hidden="true">
            p<span>g</span>
          </span>
          <span>
            People’s Guide<span className="pg-logo-dot">.</span>
          </span>
        </a>

        <div className="pg-story-content">
          <div className="pg-kicker">
            <span />
            A LITTLE CLARITY. A WAY FORWARD.
          </div>

          <h1>
            Life gets
            <br />
            complicated.
            <br />
            <span>
              Finding support
              <br />
              shouldn’t.
            </span>
          </h1>

          <p className="pg-story-description">
            A clearer path through public services.
            Start with your situation. Discover your next step.
          </p>

          <div className="pg-illustration" aria-hidden="true">
            <div className="pg-orbit pg-orbit-one" />
            <div className="pg-orbit pg-orbit-two" />
            <div className="pg-orbit pg-orbit-three" />

            <div className="pg-path-card">
              <div className="pg-path-icon">↗</div>
              <div>
                <strong>One place to begin.</strong>
                <span>Support for the things that matter.</span>
              </div>
              <span className="pg-path-spark">✦</span>
            </div>

            <span className="pg-floating pg-floating-one">
              Housing
            </span>
            <span className="pg-floating pg-floating-two">
              Wellbeing
            </span>
            <span className="pg-floating pg-floating-three">
              Money & care
            </span>
          </div>
        </div>

        <div className="pg-story-footer">
          <span className="pg-footer-line" />
          Built around people. Powered by local AI.
        </div>
      </section>

      <section className="pg-access">
        <div className="pg-top-note">
          THE RIGHT SUPPORT. ONE PLACE.
        </div>

        <div className="pg-form-wrap">
          <div className="pg-welcome-icon" aria-hidden="true">
            ↗
          </div>

          <p className="pg-overline">
            YOUR NEXT CHAPTER STARTS HERE
          </p>

          <h2>
            {registering ? "Create your account." : "Welcome back."}
          </h2>

          <p className="pg-form-description">
            {registering
              ? "Create a People’s Guide account to get started."
              : "Sign in to explore the support available to you."}
          </p>

          <form onSubmit={handleSubmit}>
            <label htmlFor="login-email">
              Email address
            </label>

            <input
              id="login-email"
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

            <label htmlFor="login-password">
              Password
            </label>

            <div className="pg-password">
              <input
                id="login-password"
                name="password"
                type={showPassword ? "text" : "password"}
                autoComplete={
                  registering ? "new-password" : "current-password"
                }
                placeholder={
                  registering
                    ? "Create a password of at least 12 characters"
                    : "Enter your password"
                }
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                minLength={registering ? 12 : 1}
                maxLength={128}
                disabled={loading}
                required
              />

              <button
                type="button"
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

            <button
              className="pg-signin"
              type="submit"
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

            {message && (
              <p className="pg-feedback" role="status">
                {message}
              </p>
            )}
          </form>

          <div className="pg-preview">
            <button
              type="button"
              className="pg-account-toggle"
              disabled={loading}
              onClick={switchMode}
            >
              {registering
                ? "Already have an account? Sign in"
                : "New here? Create an account"}
            </button>

            {registering && (
              <p>
                Use a unique password of at least 12 characters.
                Email verification and password recovery are not
                available in this prototype.
              </p>
            )}
          </div>

          <div className="pg-processing">
            <svg
              width="20"
              height="22"
              viewBox="0 0 24 26"
              fill="none"
              aria-hidden="true"
            >
              <path
                d="M12 2L21 6V12C21 18 17 22 12 24C7 22 3 18 3 12V6L12 2Z"
                stroke="currentColor"
                strokeWidth="1.6"
                strokeLinejoin="round"
              />
              <path
                d="M8 13L11 16L16 10"
                stroke="currentColor"
                strokeWidth="1.6"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>

            <div>
              <strong>
                Local intelligence. Thoughtful support.
              </strong>
              <p>
                AI processing runs on our team’s NVIDIA DGX Spark.
              </p>
            </div>
          </div>
        </div>

        <footer className="pg-access-footer">
          <span>People’s Guide</span>
          <span>Clarity. Confidence. A next step.</span>
        </footer>
      </section>
    </main>
  );
}