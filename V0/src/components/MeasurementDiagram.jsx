export default function MeasurementDiagram({ activeCategory }) {
    // This component would display a human body diagram with highlighted measurement points
    // based on the active category. For simplicity, we're using a placeholder.
  
    return (
      <div className="relative aspect-[3/4] w-full max-w-[200px] mx-auto bg-slate-100 dark:bg-slate-800 rounded-lg p-2 flex items-center justify-center">
        <div className="text-center text-sm text-slate-500 dark:text-slate-400">
          <p>Measurement diagram</p>
          <p className="font-medium mt-2 capitalize">{activeCategory.replace(/([A-Z])/g, " $1").trim()}</p>
        </div>
  
        {/* In a real implementation, you would have SVG diagrams for each category */}
        {/* Example:
        {activeCategory === 'upperBody' && (
          <svg>...</svg>
        )}
        */}
      </div>
    )
  }