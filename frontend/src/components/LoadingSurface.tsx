import { cn } from "@/lib/utils";
import { Skeleton } from "@/components/ui/skeleton";

export function LoadingDots({ className }: { className?: string }) {
  return (
    <div className={cn("flex items-center gap-1", className)}>
      <span className="h-2 w-2 animate-bounce rounded-full bg-current [animation-delay:-0.3s]" />
      <span className="h-2 w-2 animate-bounce rounded-full bg-current [animation-delay:-0.15s]" />
      <span className="h-2 w-2 animate-bounce rounded-full bg-current" />
    </div>
  );
}

export function LoadingSurface() {
  return (
    <div className="flex flex-col gap-5 animate-in fade-in-0 duration-500">
      {/* Header skeleton */}
      <div className="flex flex-col gap-2">
        <Skeleton className="h-8 w-3/5" />
        <Skeleton className="h-4 w-1/2" />
      </div>

      {/* Metric cards row */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="flex flex-col gap-2 rounded-xl bg-card p-4 shadow-sm ring-1 ring-border">
            <Skeleton className="h-3 w-16" />
            <Skeleton className="h-8 w-20" />
            <Skeleton className="h-3 w-10" />
          </div>
        ))}
      </div>

      {/* Main content blocks */}
      <div className="flex flex-col gap-3">
        <Skeleton className="h-40 w-full rounded-xl" />
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
          <Skeleton className="h-32 w-full rounded-xl" />
          <Skeleton className="h-32 w-full rounded-xl" />
        </div>
      </div>

      {/* List items */}
      <div className="flex flex-col gap-3">
        {Array.from({ length: 3 }).map((_, i) => (
          <div key={i} className="flex items-center gap-3 rounded-xl bg-card p-3 shadow-sm ring-1 ring-border">
            <Skeleton className="h-16 w-16 shrink-0 rounded-lg" />
            <div className="flex flex-1 flex-col gap-2">
              <Skeleton className="h-4 w-3/4" />
              <Skeleton className="h-3 w-1/2" />
              <Skeleton className="h-3 w-1/4" />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
