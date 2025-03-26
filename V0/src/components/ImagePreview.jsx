"use client"

import { useState } from "react"

export default function ImagePreview({ image }) {
  const [isLoading, setIsLoading] = useState(true)

  if (!image) return null

  return (
    <div className="relative mx-auto aspect-[3/4] max-h-[500px] w-full max-w-md overflow-hidden rounded-lg bg-slate-100 dark:bg-slate-900">
      <img
        src={image || "/placeholder.svg"}
        alt="Preview"
        className={`h-full w-full object-contain transition-opacity duration-300 ${isLoading ? "opacity-0" : "opacity-100"}`}
        onLoad={() => setIsLoading(false)}
      />
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-slate-300 border-t-slate-600"></div>
        </div>
      )}
    </div>
  )
}