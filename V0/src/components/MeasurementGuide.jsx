import { Card, CardContent, CardHeader, CardTitle } from "./ui/card"
import { Info } from "lucide-react"

export default function MeasurementGuide() {
  const measurementGuides = [
    {
      name: "Height",
      description:
        "Stand straight against a wall without shoes. Mark the top of your head and measure from the floor to this mark.",
      tips: "Keep your head level, looking straight ahead.",
    },
    {
      name: "Chest/Bust",
      description: "Measure around the fullest part of your chest, keeping the tape measure parallel to the floor.",
      tips: "Don't pull the tape too tight. Breathe normally.",
    },
    {
      name: "Waist",
      description: "Measure around your natural waistline, the narrowest part of your torso.",
      tips: "Keep the tape snug but not tight. Don't hold your breath or pull in your stomach.",
    },
    {
      name: "Hips",
      description: "Measure around the fullest part of your hips and buttocks.",
      tips: "Stand with feet together for an accurate measurement.",
    },
    {
      name: "Inseam",
      description: "Measure from the crotch seam to the bottom of the ankle.",
      tips: "It's easier to measure this on a pair of well-fitting pants.",
    },
  ]

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center">
          <Info className="mr-2 h-5 w-5" />
          How to Measure Yourself
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {measurementGuides.map((guide, index) => (
            <div key={index} className="border-b pb-3 last:border-0">
              <h4 className="font-medium">{guide.name}</h4>
              <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">{guide.description}</p>
              <p className="text-xs text-slate-500 dark:text-slate-500 mt-1 italic">Tip: {guide.tips}</p>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}