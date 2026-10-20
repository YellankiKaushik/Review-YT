import { notFound } from "next/navigation";
import { providerIds, type ProviderId } from "@/lib/contract";
import { ReviewReader } from "@/ui/review-reader";
export default async function ReviewPage({
  params,
  searchParams,
}: {
  params: Promise<{ video: string }>;
  searchParams: Promise<{ via?: string }>;
}) {
  const { video } = await params;
  const { via = "disabled" } = await searchParams;
  if (
    !/^[A-Za-z0-9_-]{11}$/.test(video) ||
    !providerIds.includes(via as ProviderId)
  )
    notFound();
  return (
    <main id="content">
      <ReviewReader
        key={`${video}:${via}`}
        video={video}
        provider={via as ProviderId}
      />
    </main>
  );
}
