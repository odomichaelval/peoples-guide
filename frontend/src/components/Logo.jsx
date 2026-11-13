export default function Logo({ size = 36 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" aria-hidden="true">
      <rect width="32" height="32" rx="8" fill="var(--green)" />
      <path d="M9 23V9h7.5a4.5 4.5 0 010 9H9" stroke="var(--amber)" strokeWidth="3" fill="none" strokeLinecap="round" />
    </svg>
  )
}
