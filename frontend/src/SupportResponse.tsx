import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

export type Source = {
  passage_id: string;
  title: string;
  url: string;
  retrieved_at?: string;
};

type Props = {
  reply: string;
  sources: Source[];
};

function officialUrl(value: string): string | null {
  try {
    const url = new URL(value);

    if (url.protocol !== "https:") return null;

    const host = url.hostname.toLowerCase();

    const approved = [
      "gov.uk",
      "nhs.uk",
      "nhsinform.scot",
      "nhs.wales",
      "nidirect.gov.uk",
    ];

    if (
      !approved.some(
        (domain) => host === domain || host.endsWith(`.${domain}`)
      )
    ) {
      return null;
    }

    return url.href;
  } catch {
    return null;
  }
}

export default function SupportResponse({ reply, sources }: Props) {
  const sourceMap = new Map(
    sources.map((source) => [source.passage_id, source])
  );

  const approvedUrls = new Set(
    sources
      .map((source) => officialUrl(source.url))
      .filter((url): url is string => url !== null)
  );

  // Remove the old plain-text reference appendix.
  const answer = reply.split(
    /\n\s*Retrieved reference passages\b/i
  )[0];

  // Resolve citations into links using backend source records.
  const formatted = answer.replace(
    /\[(source-[a-zA-Z0-9-]+)\]/g,
    (citation, id: string) => {
      const source = sourceMap.get(id);
      const url = source ? officialUrl(source.url) : null;

      if (!source || !url) return citation;

      const label = source.title.replace(
        /[\[\]\\<>`*_]/g,
        ""
      );

      return ` [${label}](<${url}>)`;
    }
  );

  return (
    <section className="support-response" aria-labelledby="response-title">
      <header className="response-header">
        <div>
          <span className="response-eyebrow">YOUR NEXT STEPS</span>
          <h2 id="response-title">A clearer way forward</h2>
        </div>

        <span className="response-badge">AI-generated guidance</span>
      </header>

      <div className="response-markdown">
        <ReactMarkdown
          remarkPlugins={[remarkGfm]}
          skipHtml
          components={{
            a: ({ href, children }) => {
              const url = href ? officialUrl(href) : null;

              if (!url || !approvedUrls.has(url)) {
                return <span>{children}</span>;
              }

              return (
                <a
                  className="response-source-link"
                  href={url}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  <span>{children}</span>
                  <span aria-hidden="true"> ↗</span>
                  <span className="response-sr-only">
                    {" "}(opens in a new tab)
                  </span>
                </a>
              );
            },
          }}
        >
          {formatted}
        </ReactMarkdown>
      </div>

      <p className="response-footnote">
        Source links show the retrieved reference pages. They do not
        independently verify every claim or confirm eligibility.
      </p>
    </section>
  );
}