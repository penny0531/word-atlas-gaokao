import { duck } from "./sound";

let current: HTMLAudioElement | null = null;
let token = 0;
let releaseWait: (() => void) | null = null;

export function stopAudio() {
  token++;
  const release = releaseWait;
  releaseWait = null;
  current?.pause();
  current = null;
  release?.();
  if ("speechSynthesis" in window) window.speechSynthesis.cancel();
}

/** Play a recording, falling back to the device voice. Resolves when playback ends. */
export async function play(url: string | null | undefined, text: string, accent: "uk" | "us" = "uk", rate = 1) {
  stopAudio();
  const mine = token;
  duck(true);
  try {
    return await speak(url, text, accent, rate, mine);
  } finally {
    // A replay calls stopAudio before this finally runs. Only the latest play may unduck.
    if (mine === token) duck(false);
  }
}

async function speak(url: string | null | undefined, text: string, accent: "uk" | "us", rate: number, mine: number) {
  if (mine !== token) return "stopped" as const;
  if (url) {
    const a = new Audio(url);
    a.playbackRate = rate;
    current = a;
    try {
      await a.play();
      if (mine !== token) return "stopped" as const;
      await new Promise<void>((resolve) => {
        releaseWait = resolve;
        a.onended = () => {
          if (releaseWait === resolve) releaseWait = null;
          resolve();
        };
      });
      return mine === token ? ("recorded" as const) : ("stopped" as const);
    } catch {
      if (mine !== token) return "stopped" as const;
      current = null;
    }
  }
  if (!("speechSynthesis" in window)) return "unsupported" as const;
  const u = new SpeechSynthesisUtterance(text);
  u.lang = accent === "uk" ? "en-GB" : "en-US";
  u.rate = rate * 0.95;
  const voices = speechSynthesis.getVoices().filter((v) => v.lang.replace("_", "-") === u.lang);
  const best = voices.find((v) => /premium|enhanced|natural|google/i.test(v.name)) || voices[0];
  if (best) u.voice = best;
  await new Promise<void>((r) => {
    u.onend = () => r();
    u.onerror = () => r();
    speechSynthesis.speak(u);
  });
  return mine === token ? ("device" as const) : ("stopped" as const);
}
