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

export type PlayResult = "recorded" | "device" | "stopped" | "failed" | "unsupported";

/** Play a verified recording, otherwise the device voice for this exact text. */
export async function play(url: string | null | undefined, text: string, accent: "uk" | "us" = "uk", rate = 1): Promise<PlayResult> {
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

async function speak(url: string | null | undefined, text: string, accent: "uk" | "us", rate: number, mine: number): Promise<PlayResult> {
  if (mine !== token) return "stopped";
  if (url) {
    const a = new Audio(url);
    a.playbackRate = rate;
    current = a;
    try {
      await a.play();
      if (mine !== token) return "stopped";
      await new Promise<void>((resolve) => {
        releaseWait = resolve;
        a.onended = () => {
          if (releaseWait === resolve) releaseWait = null;
          resolve();
        };
      });
      return mine === token ? "recorded" : "stopped";
    } catch {
      if (mine !== token) return "stopped";
      current = null;
    }
  }
  if (!("speechSynthesis" in window) || typeof speechSynthesis.speak !== "function") return "unsupported";
  const u = new SpeechSynthesisUtterance(text);
  u.lang = accent === "uk" ? "en-GB" : "en-US";
  u.rate = rate * 0.95;
  const voices = speechSynthesis.getVoices().filter((v) => v.lang.replace("_", "-") === u.lang);
  const best = voices.find((v) => /premium|enhanced|natural|google/i.test(v.name)) || voices[0];
  if (best) u.voice = best;
  const outcome = await new Promise<"end" | "error">((resolve) => {
    u.onend = () => resolve("end");
    u.onerror = () => resolve("error");
    try {
      speechSynthesis.speak(u);
    } catch {
      resolve("error");
    }
  });
  if (mine !== token) return "stopped";
  return outcome === "end" ? "device" : "failed";
}
