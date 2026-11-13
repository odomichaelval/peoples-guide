import { useEffect, useState } from "react";
import App from "./App";
import Login from "./Login";

export default function AuthGate() {
  const [signedIn, setSignedIn] = useState(false);
  const [checking, setChecking] = useState(true);
  const [loggingOut, setLoggingOut] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    async function checkSession() {
      try {
        const response = await fetch("/api/auth/me", {
          credentials: "same-origin",
        });

        if (active) {
          setSignedIn(response.ok);
        }
      } catch {
        if (active) {
          setSignedIn(false);
        }
      } finally {
        if (active) {
          setChecking(false);
        }
      }
    }

    checkSession();

    return () => {
      active = false;
    };
  }, []);

  async function logout() {
    if (loggingOut) return;

    setError("");
    setLoggingOut(true);

    try {
      const response = await fetch("/api/auth/logout", {
        method: "POST",
        credentials: "same-origin",
      });

      if (!response.ok) {
        throw new Error("Unable to sign out.");
      }

      setSignedIn(false);
    } catch {
      setError("Unable to sign out. Please try again.");
    } finally {
      setLoggingOut(false);
    }
  }

  if (checking) {
    return (
      <p style={{ padding: 32 }} role="status">
        Checking your session…
      </p>
    );
  }

  if (!signedIn) {
    return (
      <Login
        onSignedIn={() => {
          setError("");
          setSignedIn(true);
        }}
      />
    );
  }

  return (
    <>
      <div style={{ padding: "16px 24px", textAlign: "right" }}>
        <button
          className="example"
          onClick={logout}
          disabled={loggingOut}
        >
          {loggingOut ? "Signing out…" : "Sign out"}
        </button>

        {error && <p role="alert">{error}</p>}
      </div>

      <App />
    </>
  );
}