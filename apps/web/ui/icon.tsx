type IconName = "play" | "chart" | "link" | "layers" | "clock" | "arrow";
const paths: Record<IconName, string> = {
  play: "M9 7l8 5-8 5V7z M4 3h16a2 2 0 012 2v12a2 2 0 01-2 2H8l-5 3V5a2 2 0 011-2z",
  chart: "M4 4v16h16 M8 15v-4 M13 15V7 M18 15v-7",
  link: "M10 13a5 5 0 007 0l3-3a5 5 0 00-7-7l-2 2 M14 11a5 5 0 00-7 0l-3 3a5 5 0 007 7l2-2",
  layers: "M12 3L2 8l10 5 10-5-10-5z M2 12l10 5 10-5 M2 16l10 5 10-5",
  clock: "M12 7v5l3 2 M22 12a10 10 0 11-20 0 10 10 0 0120 0z",
  arrow: "M5 12h14 M13 6l6 6-6 6",
};
export function Icon({ name }: { name: IconName }) {
  return (
    <svg
      className="icon"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.7"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      <path d={paths[name]} />
    </svg>
  );
}
