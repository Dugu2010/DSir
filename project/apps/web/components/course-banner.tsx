"use client";

import { useState } from "react";
import { cn } from "@/lib/utils";

interface CourseBannerProps {
  title: string;
  thumbnail: string | null;
  alt: string;
  className?: string;
}

function gradientFor(title: string) {
  const hues = [220, 260, 300, 340, 20, 160, 190, 40, 120, 280];
  const hue = hues[title.length % hues.length] ?? 220;
  return {
    from: `hsl(${hue}, 80%, 55%)`,
    to: `hsl(${(hue + 40) % 360}, 80%, 45%)`,
  };
}

export function CourseBanner({
  title,
  thumbnail,
  alt,
  className,
}: CourseBannerProps) {
  const [error, setError] = useState(false);
  const fallback = gradientFor(title);

  if (error || !thumbnail) {
    return (
      <div
      className={cn(
        "flex items-center justify-center bg-gradient-to-br text-white",
        className
      )}
        style={{ backgroundImage: `linear-gradient(135deg, ${fallback.from}, ${fallback.to})` }}
        aria-label={alt}
      >
        <span className="px-4 text-center text-2xl font-bold tracking-tight drop-shadow-sm">
          {title}
        </span>
      </div>
    );
  }

  // SVG data URLs and other data URIs work best with a plain img tag.
  if (thumbnail.startsWith("data:")) {
    return (
      // eslint-disable-next-line @next/next/no-img-element
      <img
        src={thumbnail}
        alt={alt}
        className={cn("object-cover", className)}
        onError={() => setError(true)}
      />
    );
  }

  return (
    // eslint-disable-next-line @next/next/no-img-element
    <img
      src={thumbnail}
      alt={alt}
      className={cn("object-cover", className)}
      onError={() => setError(true)}
    />
  );
}
