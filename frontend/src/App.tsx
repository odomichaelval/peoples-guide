import { useState } from "react";
import "./App.css";

const TOPICS = [
  "Money and benefits",
  "Housing",
  "Health and wellbeing",
  "Work and education",
  "Disability and care",
  "Family support",
];

export default function App() {
  const [nation, setNation] = useState("");
  const [council, setCouncil] = useState("");
  const [topics, setTopics] = useState<string[]>([]);
  const [situation, setSituation] = useState("");
  const [reply, setReply] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  function toggleTopic(topic: string) {
    setTopics((current) =>
      current.includes(topic)
        ? current.filter((item) => item !== topic)
        : [...current, topic]
    );
  }

  function reset() {
    setNation("");
    setCouncil("");
    setTopics([]);
    setSituation("");
    setReply("");
    setError("");
  }

  async function getSupport() {
    if (loading) return;

    if (!nation || situation.trim().length < 10) {
      setError(
        "Choose your nation and describe your situation in at least 10 characters."
      );
      return;
    }

    setLoading(true);
    setError("");
    setReply("");

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: situation.trim(),
          nation,
          council: council.trim(),
          topics,
        }),
      });

      if (!response.ok) {
        throw new Error(
          "Unable to get guidance. Please check the backend terminal."
        );
      }

      const data = await response.json();

      if (typeof data.reply !== "string" || !data.reply.trim()) {
        throw new Error("No answer was returned. Please try again.");
      }

      setReply(data.reply);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Something went wrong."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="page">
      <header className="header">
        <a className="brand" href="/">
          People’s Guide
        </a>

        <span className="badge">Public services prototype</span>
      </header>

      <section className="hero">
        <span className="eyebrow">
          SUPPORT STARTS WITH UNDERSTANDING
        </span>

        <h1>
          Find your next step.
          <br />
          Get the support you need.
        </h1>

        <p>
          The right support. The right information. One place.
          Explore help with money, housing, health, care and more.
        </p>
      </section>

      <section className="card" aria-labelledby="form-title">
        <h2 id="form-title">Tell us what you need</h2>

        <p className="notice">
          Coverage is being developed. The current source collection
          mainly covers benefits and housing. Health guidance and
          location filtering are not connected yet.
        </p>

        <label htmlFor="nation">
          Which UK nation do you live in?
        </label>

        <select
          id="nation"
          value={nation}
          onChange={(event) => setNation(event.target.value)}
          disabled={loading}
        >
          <option value="">Choose a nation</option>
          <option value="England">England</option>
          <option value="Scotland">Scotland</option>
          <option value="Wales">Wales</option>
          <option value="Northern Ireland">Northern Ireland</option>
        </select>

        <label htmlFor="council">
          Council area or town — optional
        </label>

        <input
          id="council"
          type="text"
          value={council}
          onChange={(event) => setCouncil(event.target.value)}
          maxLength={100}
          disabled={loading}
          placeholder="For example: Sheffield or Cardiff"
        />

        <fieldset className="topic-fieldset">
          <legend>What would you like help with?</legend>

          <p className="muted">
            Choose any that apply, or leave blank.
          </p>

          <div className="topics">
            {TOPICS.map((topic) => (
              <label className="topic-option" key={topic}>
                <input
                  type="checkbox"
                  checked={topics.includes(topic)}
                  onChange={() => toggleTopic(topic)}
                  disabled={loading}
                />

                <span>{topic}</span>
              </label>
            ))}
          </div>
        </fieldset>

        <label htmlFor="situation">
          Describe your situation
        </label>

        <textarea
          id="situation"
          value={situation}
          onChange={(event) => setSituation(event.target.value)}
          maxLength={4000}
          rows={6}
          disabled={loading}
          placeholder="Tell us what is happening and what help you need."
        />

        <p className="privacy">
          Leave out names, exact addresses, bank details, National
          Insurance numbers and medical records. Share health details
          only if you choose. Your text is processed on our team’s
          DGX Spark.
        </p>

        <div className="actions">
          <button
            className="primary"
            onClick={getSupport}
            disabled={
              loading ||
              !nation ||
              situation.trim().length < 10
            }
          >
            {loading
              ? "Reviewing your situation…"
              : "Explore support"}
          </button>

          <button
            className="example"
            onClick={reset}
            disabled={loading}
          >
            Clear
          </button>
        </div>

        {error && (
          <p className="error" role="alert">
            {error}
          </p>
        )}

        <div aria-live="polite" aria-busy={loading}>
          {loading && (
            <p className="muted">
              Waiting for the local model…
            </p>
          )}

          {reply && (
            <section className="result">
              <h2>Your response</h2>
              <div className="answer">{reply}</div>
            </section>
          )}
        </div>
      </section>

      <footer>
        This prototype helps you explore services. It does not
        diagnose conditions or determine official eligibility.
      </footer>
    </main>
  );
}