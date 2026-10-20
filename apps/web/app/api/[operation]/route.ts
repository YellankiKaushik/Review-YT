import { relay } from "@/lib/relay";
export const runtime = "nodejs";
export const maxDuration = 120;
type Context = { params: Promise<{ operation: string }> };
async function handle(request: Request, context: Context) {
  const { operation } = await context.params;
  return relay(request, operation);
}
export { handle as GET, handle as POST };
