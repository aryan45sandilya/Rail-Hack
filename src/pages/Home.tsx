import React, { useState } from "react";
import { Train, MapPin, Calendar, Layers, Users, TrendingUp, HelpCircle } from "lucide-react";

interface HomeProps {
  onAnalyse: (formData: any) => void;
  quickFill: (route: { src: string; dst: string; train: string }) => void;
}

const POPULAR_QUICKS = [
  { label: "Delhi ➔ Mumbai", src: "NDLS", dst: "MMCT", train: "12951" },
  { label: "Delhi ➔ Patna", src: "NDLS", dst: "PNBE", train: "12121" },
  { label: "Bangalore ➔ Chennai", src: "SBC", dst: "MAS", train: "22691" },
  { label: "Pune ➔ Mumbai", src: "PUNE", dst: "CSMT", train: "12009" }
];

export default function Home({ onAnalyse, quickFill }: HomeProps) {
  const [trainNumber, setTrainNumber] = useState("");
  const [source, setSource] = useState("");
  const [destination, setDestination] = useState("");
  const [journeyDate, setJourneyDate] = useState("");
  const [coachClass, setCoachClass] = useState("3A");
  const [quota, setQuota] = useState("GN");
  const [wlNumber, setWlNumber] = useState("");
  
  const [error, setError] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!trainNumber.trim()) {
      setError("Please specify a Train Number (e.g., 12951)");
      return;
    }
    if (!source.trim() || source.length < 3) {
      setError("Please specify a valid Source Station code (e.g., NDLS)");
      return;
    }
    if (!destination.trim() || destination.length < 3) {
      setError("Please specify a valid Destination Station code (e.g., MMCT)");
      return;
    }
    if (!journeyDate) {
      setError("Please select a Journey Date");
      return;
    }
    if (!wlNumber || parseInt(wlNumber, 10) < 1) {
      setError("Please enter a valid Waitlist Position (e.g., 45)");
      return;
    }

    // Call analysis
    onAnalyse({
      train_number: trainNumber.trim(),
      source: source.toUpperCase().trim(),
      destination: destination.toUpperCase().trim(),
      journey_date: journeyDate,
      coach_class: coachClass,
      quota,
      initial_wl: parseInt(wlNumber, 10),
      booked_at: new Date(Date.now() - 15 * 24 * 60 * 60 * 1000).toISOString() // Simulated booking 15 days ago
    });
  };

  const handleQuickSelect = (q: typeof POPULAR_QUICKS[0]) => {
    setTrainNumber(q.train);
    setSource(q.src);
    setDestination(q.dst);
    setWlNumber(String(Math.floor(15 + Math.random() * 65)));
    
    // Future date setup (approx 15 days from now)
    const future = new Date();
    future.setDate(future.getDate() + 15);
    setJourneyDate(future.toISOString().split("T")[0]);
  };

  return (
    <div className="w-full max-w-2xl mx-auto bg-[#231f1a] border border-[#3d3530] rounded-xl p-6 md:p-8 relative overflow-hidden shadow-2xl">
      {/* Visual background element to enhance counter terminal atmosphere */}
      <div className="absolute top-0 right-0 w-32 h-32 bg-[#f5a623] opacity-[0.02] rounded-full blur-2xl pointer-events-none" />
      
      {/* Booking Counter Terminal Header */}
      <div className="flex flex-col items-center justify-center text-center pb-6 mb-6 border-b border-[#3d3530]">
        <div className="w-12 h-12 rounded-lg bg-[#f5a62315] border border-[#f5a62340] flex items-center justify-center text-[#f5a623] mb-3 select-none">
          <Train className="w-6 h-6 animate-pulse" />
        </div>
        <h2 className="text-xl font-mono text-[#f5a623] tracking-wider uppercase font-bold uppercase amber-glow">
          IRCTC TICKET COUNTER TERMINAL
        </h2>
        <p className="text-xs text-[#a89880] max-w-sm mt-1">
          Input booking descriptors to execute the high-fidelity waitlist probability model.
        </p>
      </div>

      {/* Quick Select Buttons */}
      <div className="mb-6">
        <span className="block text-[10px] font-mono text-[#5c5248] uppercase tracking-wider mb-2">
          QUICK FILL POPULAR ROUTE SEED DATA:
        </span>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
          {POPULAR_QUICKS.map((q) => (
            <button
              key={q.label}
              type="button"
              onClick={() => handleQuickSelect(q)}
              className="px-2 py-1.5 rounded bg-[#1a1612] hover:bg-[#2e2621] border border-[#3d3530] hover:border-[#f5a62330] text-[11px] font-mono text-[#a89880] hover:text-[#f5a623] transition-all text-center truncate"
            >
              {q.label}
            </button>
          ))}
        </div>
      </div>

      {error && (
        <div className="mb-5 p-3 rounded border border-red-900/30 bg-red-950/20 text-[#c0392b] text-xs font-mono text-center">
          ERROR: {error}
        </div>
      )}

      {/* Main Terminal Form */}
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-5">
          
          {/* Train Number */}
          <div className="flex flex-col">
            <label className="text-[10px] font-mono text-[#a89880] uppercase tracking-widest mb-1.5 flex items-center gap-1.5">
              <Train className="w-3.5 h-3.5 text-[#f5a623]" />
              Train Number
            </label>
            <input
              type="text"
              maxLength={5}
              placeholder="e.g. 12951"
              value={trainNumber}
              onChange={(e) => setTrainNumber(e.target.value.replace(/\D/g, ""))}
              className="bg-[#1a1612] text-[#e8e0d0] font-mono text-sm py-2 px-1 border-b border-[#3d3530] focus:border-[#f5a623] outline-none transition-colors placeholder-[#5c5248]"
            />
          </div>

          {/* Journey Date */}
          <div className="flex flex-col">
            <label className="text-[10px] font-mono text-[#a89880] uppercase tracking-widest mb-1.5 flex items-center gap-1.5">
              <Calendar className="w-3.5 h-3.5 text-[#f5a623]" />
              Journey Date
            </label>
            <input
              type="date"
              value={journeyDate}
              onChange={(e) => setJourneyDate(e.target.value)}
              className="bg-[#1a1612] text-[#e8e0d0] font-mono text-sm py-2 px-1 border-b border-[#3d3530] focus:border-[#f5a623] outline-none transition-colors placeholder-[#5c5248] calendar-dark"
            />
          </div>

          {/* Source Code */}
          <div className="flex flex-col">
            <label className="text-[10px] font-mono text-[#a89880] uppercase tracking-widest mb-1.5 flex items-center gap-1.5">
              <MapPin className="w-3.5 h-3.5 text-[#f5a623]" />
              Source Station (Code)
            </label>
            <input
              type="text"
              maxLength={4}
              placeholder="e.g. NDLS"
              value={source}
              onChange={(e) => setSource(e.target.value.toUpperCase().replace(/[^A-Za-z]/g, ""))}
              className="bg-[#1a1612] text-[#e8e0d0] font-mono text-sm py-2 px-1 border-b border-[#3d3530] focus:border-[#f5a623] outline-none transition-colors placeholder-[#5c5248]"
            />
          </div>

          {/* Destination Code */}
          <div className="flex flex-col">
            <label className="text-[10px] font-mono text-[#a89880] uppercase tracking-widest mb-1.5 flex items-center gap-1.5">
              <MapPin className="w-3.5 h-3.5 text-[#f5a623]" />
              Destination Station (Code)
            </label>
            <input
              type="text"
              maxLength={4}
              placeholder="e.g. MMCT"
              value={destination}
              onChange={(e) => setDestination(e.target.value.toUpperCase().replace(/[^A-Za-z]/g, ""))}
              className="bg-[#1a1612] text-[#e8e0d0] font-mono text-sm py-2 px-1 border-b border-[#3d3530] focus:border-[#f5a623] outline-none transition-colors placeholder-[#5c5248]"
            />
          </div>

          {/* Coach Class Selection */}
          <div className="flex flex-col">
            <label className="text-[10px] font-mono text-[#a89880] uppercase tracking-widest mb-1.5 flex items-center gap-1.5">
              <Layers className="w-3.5 h-3.5 text-[#f5a623]" />
              Coach Class
            </label>
            <select
              value={coachClass}
              onChange={(e) => setCoachClass(e.target.value)}
              className="bg-[#1a1612] text-[#e8e0d0] font-mono text-sm py-2 px-1 border-b border-[#3d3530] focus:border-[#f5a623] outline-none transition-colors"
            >
              <option value="SL">SL - Sleeper Class</option>
              <option value="3A">3A - AC 3 Tier</option>
              <option value="2A">2A - AC 2 Tier</option>
              <option value="1A">1A - AC First Class</option>
            </select>
          </div>

          {/* Quota Selection */}
          <div className="flex flex-col">
            <label className="text-[10px] font-mono text-[#a89880] uppercase tracking-widest mb-1.5 flex items-center gap-1.5">
              <Users className="w-3.5 h-3.5 text-[#f5a623]" />
              Reservation Quota
            </label>
            <select
              value={quota}
              onChange={(e) => setQuota(e.target.value)}
              className="bg-[#1a1612] text-[#e8e0d0] font-mono text-sm py-2 px-1 border-b border-[#3d3530] focus:border-[#f5a623] outline-none transition-colors"
            >
              <option value="GN">GN - General Quota</option>
              <option value="TQ">TQ - Tatkal Quota</option>
              <option value="LD">LD - Ladies Quota</option>
              <option value="SS">SS - Senior Citizen</option>
            </select>
          </div>

          {/* Waitlist Position */}
          <div className="flex flex-col sm:col-span-2">
            <label className="text-[10px] font-mono text-[#a89880] uppercase tracking-widest mb-1.5 flex items-center gap-1.5">
              <TrendingUp className="w-3.5 h-3.5 text-[#f5a623]" />
              Current Waitlist Number (WL Position)
            </label>
            <input
              type="text"
              placeholder="e.g. 45"
              value={wlNumber}
              onChange={(e) => setWlNumber(e.target.value.replace(/\D/g, ""))}
              className="bg-[#1a1612] text-[#f5a623] font-mono text-base py-2.5 px-2 border-b border-[#3d3530] focus:border-[#f5a623] outline-none transition-colors placeholder-[#5c5248] font-bold"
            />
          </div>

        </div>

        {/* Submit Button */}
        <button
          type="submit"
          className="w-full mt-4 bg-[#f5a623] hover:bg-[#e0951a] text-[#1a1612] hover:text-[#0a0807] font-mono font-bold py-3.5 rounded-lg border border-[#f5a623] hover:border-[#e0951a] tracking-wider transition-all shadow-[0_0_15px_rgba(245,166,35,0.15)] flex items-center justify-center gap-2 cursor-pointer"
        >
          ANALYSE TICKET
        </button>

        <p className="text-[10px] text-[#5c5248] font-mono text-center tracking-wide uppercase mt-3">
          ⚡ Predictions based on historical IRCTC database snapshots & Trained XGBoost classifiers
        </p>
      </form>
    </div>
  );
}
