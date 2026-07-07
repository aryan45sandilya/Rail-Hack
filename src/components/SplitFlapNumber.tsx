import { useEffect, useState } from "react";

interface SplitFlapNumberProps {
  target: number; // 0 to 100
}

interface FlapDigitProps {
  value: string;
  isFlipping: boolean;
}

function FlapDigit({ value, isFlipping }: FlapDigitProps) {
  return (
    <div className="relative flex flex-col items-center justify-center w-14 h-20 md:w-20 md:h-28 bg-[#151210] rounded-lg border border-[#3d3530] font-mono select-none overflow-hidden border-glow">
      {/* Top Half */}
      <div className="absolute top-0 left-0 w-full h-[50%] bg-[#211c18] border-b border-[#120f0c] flex items-end justify-center overflow-hidden">
        <span className="text-[#f5a623] text-4xl md:text-6xl font-bold leading-none translate-y-[50%] amber-glow">
          {value}
        </span>
      </div>

      {/* Bottom Half */}
      <div className="absolute bottom-0 left-0 w-full h-[50%] bg-[#1a1613] flex items-start justify-center overflow-hidden">
        <span className="text-[#f5a623] text-4xl md:text-6xl font-bold leading-none -translate-y-[50%] amber-glow">
          {value}
        </span>
      </div>

      {/* Mechanical Split Line */}
      <div className="absolute w-full h-[1px] bg-[#0c0a09] top-[50%] left-0 z-10 shadow-sm" />

      {/* Physical side rivets */}
      <div className="absolute left-0 top-[50%] -translate-y-1/2 w-[3px] h-[6px] bg-[#3d3530] rounded-r z-20" />
      <div className="absolute right-0 top-[50%] -translate-y-1/2 w-[3px] h-[6px] bg-[#3d3530] rounded-l z-20" />

      {/* Flip Overlay Animation */}
      {isFlipping && (
        <div className="absolute top-0 left-0 w-full h-[50%] bg-[#2a2420] border-b border-[#120f0c] flex items-end justify-center overflow-hidden animate-flap z-15">
          <span className="text-[#f5a623] text-4xl md:text-6xl font-bold leading-none translate-y-[50%] amber-glow">
            {value}
          </span>
        </div>
      )}
    </div>
  );
}

export default function SplitFlapNumber({ target }: SplitFlapNumberProps) {
  const clamped = Math.min(100, Math.max(0, Math.round(target)));
  const targetStr = String(clamped).padStart(3, "0");

  const [displayDigits, setDisplayDigits] = useState<string[]>(["0", "0", "0"]);
  const [flippingState, setFlippingState] = useState<boolean[]>([false, false, false]);

  useEffect(() => {
    let cancelled = false;

    // Reset to "000" at start of each new animation
    setDisplayDigits(["0", "0", "0"]);
    setFlippingState([false, false, false]);

    const targets = [
      parseInt(targetStr[0], 10),
      parseInt(targetStr[1], 10),
      parseInt(targetStr[2], 10),
    ];

    const animateDigit = (position: number, targetVal: number): Promise<void> => {
      return new Promise((resolve) => {
        // If target is 0, nothing to animate — just resolve immediately
        if (targetVal === 0) {
          resolve();
          return;
        }

        let current = 0;

        // Stagger start: each digit starts 200ms after the previous
        const startDelay = position * 200;

        setTimeout(() => {
          if (cancelled) { resolve(); return; }

          const interval = setInterval(() => {
            if (cancelled) {
              clearInterval(interval);
              resolve();
              return;
            }

            current += 1;

            const displayVal = current % 10; // visual digit cycles 0-9
            setDisplayDigits((prev) => {
              const next = [...prev];
              next[position] = String(displayVal);
              return next;
            });
            setFlippingState((prev) => {
              const next = [...prev];
              next[position] = true;
              return next;
            });

            if (current === targetVal) {
              clearInterval(interval);
              // Lock in final value and stop flipping
              setDisplayDigits((prev) => {
                const next = [...prev];
                next[position] = String(targetVal);
                return next;
              });
              setFlippingState((prev) => {
                const next = [...prev];
                next[position] = false;
                return next;
              });
              resolve();
            }
          }, 60);
        }, startDelay);
      });
    };

    Promise.all(targets.map((t, i) => animateDigit(i, t)));

    return () => {
      cancelled = true;
    };
  }, [clamped]);

  const showHundreds = clamped >= 100;
  const showTens = clamped >= 10;

  return (
    <div className="flex items-center gap-2 justify-center py-4 bg-[#1e1915] px-6 rounded-xl border border-[#352e2a]">
      {showHundreds && (
        <FlapDigit value={displayDigits[0]} isFlipping={flippingState[0]} />
      )}
      {showTens && (
        <FlapDigit value={displayDigits[1]} isFlipping={flippingState[1]} />
      )}
      <FlapDigit value={displayDigits[2]} isFlipping={flippingState[2]} />

      {/* Percentage Sign */}
      <div className="relative flex flex-col items-center justify-center w-14 h-20 md:w-20 md:h-28 bg-[#151210] rounded-lg border border-[#3d3530] font-mono select-none overflow-hidden border-glow">
        <div className="absolute top-0 left-0 w-full h-[50%] bg-[#211c18] border-b border-[#120f0c] flex items-end justify-center overflow-hidden">
          <span className="text-[#f5a623] text-4xl md:text-6xl font-bold leading-none translate-y-[50%] amber-glow">%</span>
        </div>
        <div className="absolute bottom-0 left-0 w-full h-[50%] bg-[#1a1613] flex items-start justify-center overflow-hidden">
          <span className="text-[#f5a623] text-4xl md:text-6xl font-bold leading-none -translate-y-[50%] amber-glow">%</span>
        </div>
        <div className="absolute w-full h-[1px] bg-[#0c0a09] top-[50%] left-0 z-10 shadow-sm" />
      </div>
    </div>
  );
}
