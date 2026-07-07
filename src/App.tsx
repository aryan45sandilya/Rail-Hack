import { useState } from "react";
import { Train, Activity, RefreshCw, Terminal, Compass, Hash } from "lucide-react";
import Home from "./pages/Home";
import Result from "./pages/Result";
import Explorer from "./pages/Explorer";
import PNRStatus from "./pages/PNRStatus";

type ActiveScreen = "home" | "result" | "explorer" | "pnr";

export default function App() {
  const [activeScreen, setActiveScreen] = useState<ActiveScreen>("home");
  const [formData, setFormData] = useState<any>(null);
  const [predictionResult, setPredictionResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [loadingStep, setLoadingStep] = useState("");

  const handleAnalyseTicket = async (data: any) => {
    setLoading(true);
    setFormData(data);
    
    // Simulate mechanical railway diagnostic scanner delay sequence
    const steps = [
      "ESTABLISHING SECURE GATEWAY CONNECTION...",
      "FETCHING HISTORICAL ROUTE DECAY Snapshots...",
      "CORRELATING WITH SEASONAL FESTIVAL PEAKS...",
      "EXECUTING TENSOR GRADIENT XGBOOST CLASSIFIER...",
      "CONFIRMATION PROBABILITY CALCULATED!"
    ];

    for (let i = 0; i < steps.length; i++) {
      setLoadingStep(steps[i]);
      await new Promise((resolve) => setTimeout(resolve, i === 3 ? 600 : 350));
    }

    try {
      const response = await fetch("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
      });

      if (response.ok) {
        const result = await response.json();
        setPredictionResult(result);
        setActiveScreen("result");
      } else {
        const err = await response.json();
        console.error("API error", err);
        alert(`Prediction Error: ${err.error || "Failed to analyze ticket"}`);
      }
    } catch (err) {
      console.error("Network error", err);
      alert("Network Connection Failure. Unable to communicate with prediction service.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#1a1612] text-[#e8e0d0] flex flex-col station-grid relative pb-12 overflow-x-hidden select-none">
      
      {/* Station Terminal Top Main Header Board */}
      <header className="border-b-4 border-[#f5a623] bg-[#231f1a] shadow-lg sticky top-0 z-50">
        <div className="max-w-5xl mx-auto px-4 md:px-6 py-4 flex flex-col sm:flex-row items-center justify-between gap-4">
          
          {/* Logo Brand Zone */}
          <div className="flex items-center gap-3">
            <div className="relative flex items-center justify-center w-10 h-10 bg-[#1a1612] border-2 border-[#f5a623] rounded select-none">
              <Train className="w-5.5 h-5.5 text-[#f5a623] animate-pulse" />
              {/* Corner rivets */}
              <div className="absolute top-0.5 left-0.5 w-1 h-1 rounded-full bg-[#3d3530]" />
              <div className="absolute top-0.5 right-0.5 w-1 h-1 rounded-full bg-[#3d3530]" />
              <div className="absolute bottom-0.5 left-0.5 w-1 h-1 rounded-full bg-[#3d3530]" />
              <div className="absolute bottom-0.5 right-0.5 w-1 h-1 rounded-full bg-[#3d3530]" />
            </div>
            <div className="text-left">
              <h1 className="text-xl font-mono font-bold text-[#f5a623] tracking-widest leading-none uppercase amber-glow">
                RAILHACK
              </h1>
              <span className="text-[10px] text-[#a89880] uppercase tracking-wider block font-mono mt-1">
                WAITLIST INTELLIGENCE ENGINE
              </span>
            </div>
          </div>

          {/* Navigation Tab Command Blocks */}
          <nav className="flex items-center gap-2 font-mono text-xs">
            <button
              onClick={() => {
                setActiveScreen("home");
                setPredictionResult(null);
              }}
              className={`px-3 py-2 border rounded-md uppercase tracking-wider flex items-center gap-1.5 transition-all duration-150 cursor-pointer ${
                activeScreen === "home" || activeScreen === "result"
                  ? "bg-[#f5a623] text-[#1a1612] border-[#f5a623] font-bold shadow-[0_0_12px_rgba(245,166,35,0.25)]"
                  : "bg-transparent text-[#a89880] hover:text-[#e8e0d0] border-[#3d3530] hover:border-[#f5a62340]"
              }`}
            >
              <Terminal className="w-3.5 h-3.5" />
              Counter Terminal
            </button>
            <button
              onClick={() => setActiveScreen("explorer")}
              className={`px-3 py-2 border rounded-md uppercase tracking-wider flex items-center gap-1.5 transition-all duration-150 cursor-pointer ${
                activeScreen === "explorer"
                  ? "bg-[#f5a623] text-[#1a1612] border-[#f5a623] font-bold shadow-[0_0_12px_rgba(245,166,35,0.25)]"
                  : "bg-transparent text-[#a89880] hover:text-[#e8e0d0] border-[#3d3530] hover:border-[#f5a62340]"
              }`}
            >
              <Compass className="w-3.5 h-3.5" />
              Route Explorer
            </button>
            <button
              onClick={() => setActiveScreen("pnr")}
              className={`px-3 py-2 border rounded-md uppercase tracking-wider flex items-center gap-1.5 transition-all duration-150 cursor-pointer ${
                activeScreen === "pnr"
                  ? "bg-[#f5a623] text-[#1a1612] border-[#f5a623] font-bold shadow-[0_0_12px_rgba(245,166,35,0.25)]"
                  : "bg-transparent text-[#a89880] hover:text-[#e8e0d0] border-[#3d3530] hover:border-[#f5a62340]"
              }`}
            >
              <Hash className="w-3.5 h-3.5" />
              PNR Status
            </button>
          </nav>

        </div>
      </header>

      {/* Main Container Stage */}
      <main className="flex-1 max-w-5xl w-full mx-auto px-4 md:px-6 py-8 relative">
        {loading ? (
          /* High Fidelity Scanning Diagnostic Display Loader */
          <div className="w-full max-w-md mx-auto bg-[#151210] border-2 border-[#f5a62340] rounded-xl p-8 text-center space-y-6 flex flex-col items-center justify-center py-16 shadow-2xl relative overflow-hidden border-glow">
            {/* Spinning radar graphic */}
            <div className="relative flex items-center justify-center w-16 h-16 bg-[#231f1a] rounded-full border border-[#3d3530]">
              <RefreshCw className="w-8 h-8 text-[#f5a623] animate-spin" />
              <div className="absolute inset-0 rounded-full border-2 border-dashed border-[#f5a623] opacity-25 animate-ping" />
            </div>

            <div className="space-y-2">
              <span className="text-[10px] font-mono text-[#5c5248] uppercase tracking-widest block">
                DIAGNOSTIC TELEMETRY ACTIVE
              </span>
              <h3 className="text-sm font-mono text-[#f5a623] font-bold tracking-wide uppercase max-w-xs leading-relaxed amber-glow">
                {loadingStep}
              </h3>
            </div>

            <div className="w-full h-1.5 bg-[#1e1915] rounded-full overflow-hidden border border-[#3d3530]">
              <div className="h-full bg-[#f5a623] animate-pulse" style={{ width: "80%" }} />
            </div>
            
            <p className="text-[9px] font-mono text-[#5c5248] uppercase">
              TRANSACTION REFERENCE: {Math.floor(100000 + Math.random() * 900000)}
            </p>
          </div>
        ) : (
          /* Render Active Screen View */
          <>
            {activeScreen === "home" && (
              <Home
                onAnalyse={handleAnalyseTicket}
                quickFill={handleAnalyseTicket}
              />
            )}
            
            {activeScreen === "result" && predictionResult && formData && (
              <Result
                formData={formData}
                result={predictionResult}
                onBack={() => {
                  setActiveScreen("home");
                  setPredictionResult(null);
                }}
              />
            )}
            
            {activeScreen === "explorer" && (
              <Explorer />
            )}

            {activeScreen === "pnr" && (
              <PNRStatus />
            )}
          </>
        )}
      </main>

      {/* Persistent Status Bar (Bottom rail footer styled like physical board) */}
      <footer className="max-w-5xl w-full mx-auto px-4 md:px-6 pt-6 mt-auto border-t border-[#3d3530] flex flex-col md:flex-row justify-between items-center gap-3 text-[10px] font-mono text-[#5c5248] uppercase tracking-widest">
        <span>© 2026 RAILHACK PREDICTOR ENGINE</span>
        <span className="flex items-center gap-1">
          <Activity className="w-3.5 h-3.5 text-[#27ae60]" />
          ALL TELEMETRY SERVICES ONLINE
        </span>
      </footer>

    </div>
  );
}
