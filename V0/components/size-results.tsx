"use client"

import { useState } from "react"
import Image from "next/image"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { Button } from "@/components/ui/button"
import { Download, Info, Share2 } from "lucide-react"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "@/components/ui/tooltip"

interface Measurement {
  value: number
  unit: string
}

interface SizeResultsProps {
  results: {
    measurements: {
      chest: Measurement
      waist: Measurement
      hips: Measurement
      inseam: Measurement
      shoulder: Measurement
    }
    sizeRecommendations: {
      tops: string
      bottoms: string
      dresses: string
      shoes: string
    }
  }
  image: string | null
}

export default function SizeResults({ results, image }: SizeResultsProps) {
  const [activeTab, setActiveTab] = useState("measurements")

  const { measurements, sizeRecommendations } = results

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-6 md:flex-row">
        {image && (
          <div className="relative mx-auto aspect-[3/4] h-[300px] w-full max-w-[200px] overflow-hidden rounded-lg bg-slate-100 dark:bg-slate-900 md:mx-0">
            <Image src={image || "/placeholder.svg"} alt="Analyzed photo" fill className="object-cover" />
            <div className="absolute inset-0 bg-gradient-to-t from-black/50 to-transparent"></div>
            <div className="absolute bottom-0 left-0 right-0 p-3 text-center text-white">
              <p className="text-xs font-medium">Analyzed Image</p>
            </div>
          </div>
        )}
        <div className="flex-1">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="measurements">Measurements</TabsTrigger>
              <TabsTrigger value="recommendations">Size Recommendations</TabsTrigger>
            </TabsList>
            <TabsContent value="measurements" className="space-y-4 pt-4">
              <div className="rounded-md border p-4">
                <div className="mb-4 flex items-center justify-between">
                  <h3 className="text-lg font-medium">Body Measurements</h3>
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Button variant="ghost" size="icon" className="h-8 w-8">
                          <Info className="h-4 w-4" />
                          <span className="sr-only">Measurement Info</span>
                        </Button>
                      </TooltipTrigger>
                      <TooltipContent>
                        <p className="max-w-xs text-sm">
                          These measurements are estimated based on image analysis and may vary slightly from actual
                          measurements.
                        </p>
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                </div>
                <div className="space-y-3">
                  {Object.entries(measurements).map(([key, { value, unit }]) => (
                    <div key={key} className="flex items-center justify-between">
                      <span className="capitalize text-slate-600 dark:text-slate-400">{key}</span>
                      <span className="font-medium">
                        {value} {unit}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            </TabsContent>
            <TabsContent value="recommendations" className="space-y-4 pt-4">
              <div className="rounded-md border p-4">
                <div className="mb-4 flex items-center justify-between">
                  <h3 className="text-lg font-medium">Recommended Sizes</h3>
                  <TooltipProvider>
                    <Tooltip>
                      <TooltipTrigger asChild>
                        <Button variant="ghost" size="icon" className="h-8 w-8">
                          <Info className="h-4 w-4" />
                          <span className="sr-only">Size Info</span>
                        </Button>
                      </TooltipTrigger>
                      <TooltipContent>
                        <p className="max-w-xs text-sm">
                          Size recommendations are based on standard sizing charts and may vary by brand.
                        </p>
                      </TooltipContent>
                    </Tooltip>
                  </TooltipProvider>
                </div>
                <div className="grid grid-cols-2 gap-3">
                  {Object.entries(sizeRecommendations).map(([key, value]) => (
                    <Card key={key} className="border-0 shadow-none">
                      <CardHeader className="p-3 pb-1">
                        <CardTitle className="text-sm capitalize">{key}</CardTitle>
                      </CardHeader>
                      <CardContent className="p-3 pt-0">
                        <p className="text-2xl font-bold">{value}</p>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            </TabsContent>
          </Tabs>
        </div>
      </div>
      <Separator />
      <div className="flex flex-wrap justify-between gap-3">
        <div>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Results generated on {new Date().toLocaleDateString()}
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <Download className="mr-2 h-4 w-4" />
            Save Results
          </Button>
          <Button variant="outline" size="sm">
            <Share2 className="mr-2 h-4 w-4" />
            Share
          </Button>
        </div>
      </div>
    </div>
  )
}