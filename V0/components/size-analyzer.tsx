"use client"

import type React from "react"

import { useState, useRef } from "react"
import { Upload, RefreshCw, Check } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Progress } from "@/components/ui/progress"
import ImagePreview from "@/components/image-preview"
import SizeResults from "@/components/size-results"

export default function SizeAnalyzer() {
  const [image, setImage] = useState<string | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [progress, setProgress] = useState(0)
  const [results, setResults] = useState<any | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (event) => {
        setImage(event.target?.result as string)
        setResults(null)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    const file = e.dataTransfer.files?.[0]
    if (file) {
      const reader = new FileReader()
      reader.onload = (event) => {
        setImage(event.target?.result as string)
        setResults(null)
      }
      reader.readAsDataURL(file)
    }
  }

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
  }

  const analyzeImage = () => {
    if (!image) return

    setIsAnalyzing(true)
    setProgress(0)

    // Simulate analysis progress
    const interval = setInterval(() => {
      setProgress((prev) => {
        const newProgress = prev + Math.random() * 15
        if (newProgress >= 100) {
          clearInterval(interval)
          setTimeout(() => {
            setIsAnalyzing(false)
            // Mock results - in a real app, this would come from your analysis algorithm
            setResults({
              measurements: {
                chest: { value: 102, unit: "cm" },
                waist: { value: 84, unit: "cm" },
                hips: { value: 106, unit: "cm" },
                inseam: { value: 81, unit: "cm" },
                shoulder: { value: 46, unit: "cm" },
              },
              sizeRecommendations: {
                tops: "L",
                bottoms: "M/L",
                dresses: "L",
                shoes: "42 EU / 9 US",
              },
            })
          }, 500)
          return 100
        }
        return newProgress
      })
    }, 200)
  }

  const resetAnalysis = () => {
    setImage(null)
    setResults(null)
    setIsAnalyzing(false)
    setProgress(0)
    if (fileInputRef.current) {
      fileInputRef.current.value = ""
    }
  }

  return (
    <Card className="overflow-hidden bg-white shadow-lg dark:bg-slate-800">
      <Tabs defaultValue="upload" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="upload">Upload Photo</TabsTrigger>
          <TabsTrigger value="results" disabled={!results}>
            Results
          </TabsTrigger>
        </TabsList>
        <TabsContent value="upload" className="p-0">
          <CardContent className="p-6">
            {!image ? (
              <div
                className="flex min-h-[400px] cursor-pointer flex-col items-center justify-center rounded-lg border-2 border-dashed border-slate-300 bg-slate-50 p-12 text-center dark:border-slate-700 dark:bg-slate-900"
                onClick={() => fileInputRef.current?.click()}
                onDrop={handleDrop}
                onDragOver={handleDragOver}
              >
                <Upload className="mb-4 h-12 w-12 text-slate-400" />
                <h3 className="mb-2 text-xl font-medium text-slate-900 dark:text-slate-100">Upload a photo</h3>
                <p className="mb-4 text-sm text-slate-500 dark:text-slate-400">
                  Drag and drop or click to select a photo
                </p>
                <Button variant="outline" onClick={() => fileInputRef.current?.click()}>
                  Select Photo
                </Button>
                <input type="file" ref={fileInputRef} onChange={handleFileChange} accept="image/*" className="hidden" />
                <p className="mt-4 text-xs text-slate-400 dark:text-slate-500">
                  For best results, use a full-body photo with a neutral background
                </p>
              </div>
            ) : (
              <div className="space-y-6">
                <ImagePreview image={image} />
                <div className="flex flex-wrap gap-3">
                  {!isAnalyzing && !results ? (
                    <>
                      <Button onClick={analyzeImage} className="flex-1">
                        Analyze Photo
                      </Button>
                      <Button variant="outline" onClick={resetAnalysis}>
                        Choose Different Photo
                      </Button>
                    </>
                  ) : isAnalyzing ? (
                    <div className="w-full space-y-3">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium">Analyzing image...</span>
                        <span className="text-sm text-slate-500">{Math.round(progress)}%</span>
                      </div>
                      <Progress value={progress} className="h-2 w-full" />
                    </div>
                  ) : (
                    <div className="flex w-full items-center justify-between">
                      <div className="flex items-center gap-2 text-green-600 dark:text-green-500">
                        <Check className="h-5 w-5" />
                        <span className="font-medium">Analysis complete</span>
                      </div>
                      <Button variant="outline" size="sm" onClick={resetAnalysis}>
                        <RefreshCw className="mr-2 h-4 w-4" />
                        Start Over
                      </Button>
                    </div>
                  )}
                </div>
              </div>
            )}
          </CardContent>
        </TabsContent>
        <TabsContent value="results" className="p-0">
          {results && (
            <CardContent className="p-6">
              <SizeResults results={results} image={image} />
            </CardContent>
          )}
        </TabsContent>
      </Tabs>
    </Card>
  )
}