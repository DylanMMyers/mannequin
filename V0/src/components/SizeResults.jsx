"use client"

import { useState } from "react"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs"
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card"
import { Separator } from "./ui/separator"
import { Button } from "./ui/button"
import { Download, Info, Share2 } from "lucide-react"
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from "./ui/tooltip"

export default function SizeResults({ results, image }) {
  const [activeTab, setActiveTab] = useState("measurements")
  const [activeMeasurementCategory, setActiveMeasurementCategory] = useState("upperBody")
  const [expandedCategories, setExpandedCategories] = useState({
    upperBody: true,
    arms: false,
    torso: false,
    legs: false,
    other: false,
  })

  const { measurements, sizeRecommendations } = results
const categoryLabels = {
    upperBody: "Upper Body",
    arms: "Arms",
    torso: "Torso",
    waist: "Waist & Hips",
    legs: "Legs",
    other: "Other Measurements",
  }

  const toggleCategory = (category) => {
    setExpandedCategories({
      ...expandedCategories,
      [category]: !expandedCategories[category],
    })
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-6 md:flex-row">
        {image && (
          <div className="relative mx-auto aspect-[3/4] h-[300px] w-full max-w-[200px] overflow-hidden rounded-lg bg-slate-100 dark:bg-slate-900 md:mx-0">
            <img src={image || "/placeholder.svg"} alt="Analyzed photo" className="h-full w-full object-cover" />
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

                <Tabs value={activeMeasurementCategory} onValueChange={setActiveMeasurementCategory} className="w-full">
                  <TabsList className="mb-4 flex w-full flex-wrap gap-1">
                    {Object.keys(measurements).map((category) => (
                      <TabsTrigger key={category} value={category} className="flex-1 min-w-[100px]">
                        {categoryLabels[category] || category}
                      </TabsTrigger>
                    ))}
                  </TabsList>

                  {Object.keys(measurements).map((category) => (
                    <TabsContent key={category} value={category} className="space-y-3">
                      <div className="space-y-3">
                        {Object.entries(measurements[category]).map(([key, data]) => (
                          <div key={key} className="flex items-center justify-between border-b pb-2 last:border-0">
                            <div>
                              <span className="capitalize text-slate-800 dark:text-slate-200">
                                {key.replace(/_/g, " ")}
                              </span>
                              <TooltipProvider>
                                <Tooltip>
                                  <TooltipTrigger asChild>
                                    <Button variant="ghost" size="icon" className="h-6 w-6 ml-1">
                                      <Info className="h-3 w-3" />
                                    </Button>
                                  </TooltipTrigger>
                                  <TooltipContent>
                                    <p className="max-w-xs text-sm">{data.description}</p>
                                  </TooltipContent>
                                </Tooltip>
                              </TooltipProvider>
                            </div>
                            <span className="font-medium">
                              {data.value} {data.unit}
                            </span>
                          </div>
                        ))}
                      </div>
                    </TabsContent>
                  ))}
                </Tabs>
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
                <div className="grid grid-cols-2 gap-3 md:grid-cols-3">
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

              <div className="rounded-md border p-4">
                <h3 className="mb-3 text-lg font-medium">Size Chart Reference</h3>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50 dark:bg-gray-800">
                      <tr>
                        <th
                          scope="col"
                          className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-300"
                        >
                          Size
                        </th>
                        <th
                          scope="col"
                          className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-300"
                        >
                          Chest (cm)
                        </th>
                        <th
                          scope="col"
                          className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-300"
                        >
                          Waist (cm)
                        </th>
                        <th
                          scope="col"
                          className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider dark:text-gray-300"
                        >
                          Hips (cm)
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200 dark:bg-gray-900 dark:divide-gray-700">
                      <tr>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">XS</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">82-86</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">68-72</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">88-92</td>
                      </tr>
                      <tr>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">S</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">86-94</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">72-80</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">92-98</td>
                      </tr>
                      <tr>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">M</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">94-102</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">80-88</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">98-104</td>
                      </tr>
                      <tr>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">L</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">102-110</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">88-96</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">104-110</td>
                      </tr>
                      <tr>
                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">XL</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">110-118</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">96-104</td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm">110-118</td>
                      </tr>
                    </tbody>
                  </table>
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