import React from "react"
import type { Metadata } from "next"
import SizeAnalyzer from "../components/size-analyzer"

export const metadata: Metadata = {
  title: "Size Analyzer",
  description: "Upload a photo to analyze body measurements and get size recommendations",
}

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100 dark:from-slate-950 dark:to-slate-900">
      <div className="container mx-auto px-4 py-8 md:py-16">
        <div className="mx-auto max-w-4xl">
          <div className="mb-8 text-center">
            <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-slate-50 md:text-5xl">
              Size Analyzer
            </h1>
            <p className="mt-4 text-lg text-slate-600 dark:text-slate-400">
              Upload a photo to analyze body measurements and get size recommendations
            </p>
          </div>
          <SizeAnalyzer />
        </div>
      </div>
    </main>
  )
}