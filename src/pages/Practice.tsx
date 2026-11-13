import { Headphones, Keyboard, RotateCcw, Type } from "lucide-react";
import { useEffect, useMemo, useRef, useState, type PointerEvent } from "react";
import { prefetch, useAtlas } from "../atlas/context";
import type { Entry } from "../atlas/types";
import { play, stopAudio, type PlayResult } from "../lib/audio";
import { exampleAudioUrl, exampleClipAccent } from "../lib/sentenceAudio";
import { cue } from "../lib/sound";
import { hashSeed, shuffle } from "../lib/text";
import { clean, commitAtEnd, correctCharacterCount, resetDictationItem, same, showDictationAnswer, typingDelta, typingMetrics, typingSlots } from "../lib/typing";
import { store, useStore } from "../store/store";
import { AmbiencePicker } from "../ui/Ambience";
import { Illustration } from "../ui/Illustration";

type Mode = "word" | "sentence" | "dictation";
type Source = "recent" | "mistakes" | "saved" | "path";

const MODES: [Mode, string, string, typeof Type][] = [
  ["word", "单词", "看图写出单词", Type],
  ["sentence", "例句", "照着抄写，练出手感", Keyboard],
  ["dictation", "听写", "只听声音，写下整句", Headphones],
];
const SOURCES: [Source, string][] = [
  ["recent", "最近学过"],
  ["mistakes", "错词本"],
  ["saved", "收藏"],
  ["path", "学习路线"],
];

export function Practice() {
  const atlas = useAtlas();
  const progress = useStore((s) => s.progress);
  const startLevel = useStore((s) => s.settings.startLevel);
  const [mode, setMode] = useState<Mode>("word");
  const [source, setSource] = useState<Source>(() => (Object.keys(progress.cards).length ? "recent" : "path"));
  const [round, setRound] = useState<{ entries: Entry[]; key: number } | null>(null);

  const pool = useMemo(() => {
    const learned = Object.entries(progress.cards)
      .sort((a, b) => (b[1].last ?? 0) - (a[1].last ?? 0))
      .map(([id]) => id);
    const ids =
      source === "recent" ? learned : source === "mistakes" ? progress.mistakes : source === "saved" ? progress.bookmarks : atlas.words.filter((w) => w.cefr >= startLevel).slice(0, 400).map((w) => w.id);
    return ids.filter((id) => atlas.byId.has(id));
  }, [atlas, progress.cards, progress.mistakes, progress.bookmarks, source, startLevel]);

  const start = async () => {
    const ids = shuffle(pool.slice(0, 60), hashSeed(String(Date.now()))).slice(0, 10);
    const entries = (await prefetch(atlas, ids)).filter((e): e is Entry => !!e && (mode === "word" || e.ex.length > 0));
    if (entries.length) setRound({ entries, key: Date.now() });
  };

  if (round) return <TypingRound key={round.key} mode={mode} entries={round.entries} onExit={() => setRound(null)} onAgain={start} />;

  const best = progress.typing.filter((t) => t.mode === mode).reduce((m, t) => Math.max(m, t.wpm), 0);
  return (
    <div className="page practice">
      <header className="page-head">
        <p className="eyebrow">练习 · Typing Studio</p>
        <h1 className="display">让手，也记住它们。</h1>
        <p className="lede">打字只练拼写和手感，不会改动记忆进度。</p>
      </header>
      <div className="practice-grid">
        <section className="panel">
          <h3 className="eyebrow">模式</h3>
          <div className="mode-cards">
            {MODES.map(([k, name, desc, Icon]) => (
              <button key={k} className={`mode-card ${mode === k ? "is-on" : ""}`} onClick={() => setMode(k)} aria-pressed={mode === k}>
                <Icon size={22} strokeWidth={1.7} />
                <b>{name}</b>
                <small>{desc}</small>
              </button>
            ))}
          </div>
          <h3 className="eyebrow">词来自</h3>
          <div className="segmented segmented-wide">
            {SOURCES.map(([k, label]) => (
              <button key={k} className={source === k ? "is-on" : ""} onClick={() => setSource(k)} aria-pressed={source === k}>
                {label}
              </button>
            ))}
          </div>
          <p className="muted">
            {pool.length
              ? source === "path"
                ? "从学习路线的前 400 个词里随机抽 10 个。"
                : `可练 ${pool.length} 个词，每轮随机 10 个。`
              : "这里还没有词，先去学几个，或换个来源。"}
          </p>
          <button className="btn btn-primary btn-xl" onClick={start} disabled={!pool.length}>
            开始一轮
          </button>
        </section>
        <section className="panel practice-side">
          <img src={`${import.meta.env.BASE_URL}brand/${mode === "dictation" ? "listen" : "typing"}.webp`} alt="" />
          <dl className="mini-stats">
            <div>
              <dt>最佳速度</dt>
              <dd>
                {best}
                <small>WPM</small>
              </dd>
            </div>
            <div>
              <dt>完成轮次</dt>
              <dd>{progress.typing.length}</dd>
            </div>
          </dl>
          <p className="muted">WPM 按标准每 5 个字符计 1 词，只统计正确输入。</p>
        </section>
      </div>
    </div>
  );
}

function TypingRound({ mode, entries, onExit, onAgain }: { mode: Mode; entries: Entry[]; onExit: () => void; onAgain: () => void }) {
  const atlas = useAtlas();
  const settings = useStore((s) => s.settings);
  const [i, setI] = useState(0);
  const [value, setValue] = useState("");
  // Running totals live in a ref so every keystroke is counted exactly once.
  const totalsRef = useRef({ typed: 0, correct: 0, accepted: 0, ms: 0 });
  const [totals, setTotals] = useState(totalsRef.current);
  const [done, setDone] = useState(false);
  const [revealed, setRevealed] = useState(false);
  const [voiceNote, setVoiceNote] = useState<string | null>(null);
  const started = useRef<number | null>(null);
  const input = useRef<HTMLInputElement>(null);
  const composing = useRef(false);
  const valueRef = useRef("");
  const beforeComposition = useRef("");
  const skipRaw = useRef<string | null>(null);
  const e = entries[i];
  const target = mode === "word" ? e.w : e.ex[0].en;

  useEffect(() => {
    const fresh = resetDictationItem();
    valueRef.current = fresh.value;
    setValue(fresh.value);
    setRevealed(fresh.revealed);
    setVoiceNote(null);
    started.current = null;
    input.current?.focus();
    if (mode === "dictation") void speakSentence();
    if (mode === "word" && settings.autoplay) void play(atlas.audio(e, settings.accent), e.w, settings.accent);
  }, [i]); // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => () => stopAudio(), []);

  const snapCaret = () => {
    const el = input.current;
    if (!el || composing.current) return;
    const end = el.value.length;
    if (el.selectionStart === end && el.selectionEnd === end) return;
    el.setSelectionRange(end, end);
  };

  const onChange = (raw: string) => {
    if (done) return;
    if (composing.current) {
      valueRef.current = raw;
      setValue(raw);
      return;
    }
    const prev = valueRef.current;
    const next = commitAtEnd(prev, raw);
    if (next === prev) return;
    if (started.current === null && next) started.current = performance.now();
    const d = typingDelta(prev, next, target);
    if (settings.sfx && d.total > 0) void cue("key");
    const t = totalsRef.current;
    totalsRef.current = { ...t, typed: t.typed + d.total, correct: t.correct + d.correct };
    setTotals(totalsRef.current);
    valueRef.current = next;
    setValue(next);
    if (clean(next).length >= clean(target).length && same(next.trimEnd(), target)) finishItem(next);
  };

  const noteFor = (result: PlayResult) =>
    result === "failed" || result === "unsupported" ? "这台设备读不出这句。可以看中文，或点「看答案」。" : null;

  const speakSentence = async () => {
    const result = await play(exampleAudioUrl(atlas, e, 0), e.ex[0].en, exampleClipAccent(e.id, 0) ?? settings.accent);
    if (result === "stopped") return;
    setVoiceNote(noteFor(result));
  };

  const replay = () => {
    void speakSentence();
  };

  const reveal = () => {
    const shown = showDictationAnswer(valueRef.current);
    setRevealed(shown.revealed);
    if (shown.advance) finishItem(valueRef.current);
  };

  const pressControl = (ev: PointerEvent<HTMLButtonElement>, action: () => void) => {
    if (ev.button !== 0) return;
    ev.preventDefault();
    ev.stopPropagation();
    action();
  };

  const finishItem = (final: string) => {
    const ms = started.current ? performance.now() - started.current : 0;
    const accepted = correctCharacterCount(final, target);
    if (settings.sfx) void cue("correct");
    const t = totalsRef.current;
    const nt = { ...t, accepted: t.accepted + accepted, ms: t.ms + ms };
    totalsRef.current = nt;
    setTotals(nt);
    if (i + 1 >= entries.length) {
      setDone(true);
      const m = typingMetrics(nt.correct, nt.typed, nt.accepted, nt.ms);
      store.progress((p) => ({ ...p, typing: [...p.typing, { at: Date.now(), mode, items: entries.length, wpm: m.wpm, accuracy: m.accuracy }].slice(-500) }));
    } else window.setTimeout(() => setI(i + 1), 260);
  };

  const m = typingMetrics(totals.correct, totals.typed, totals.accepted, totals.ms);
  const chars = Array.from(clean(target));
  const typed = Array.from(clean(value));
  const slots = typingSlots(value, target);

  if (done)
    return (
      <div className="page practice">
        <section className="panel typing-done">
          <p className="eyebrow">本轮完成</p>
          <h1 className="display">
            {m.wpm} <small>WPM</small>
          </h1>
          <p className="lede">准确率 {m.accuracy}% · {entries.length} 项</p>
          <div className="summary-actions">
            <button className="btn btn-ghost" onClick={onExit}>
              返回
            </button>
            <button className="btn btn-primary btn-xl" onClick={onAgain} autoFocus>
              <RotateCcw size={18} /> 再来一轮
            </button>
          </div>
        </section>
      </div>
    );

  return (
    <div className="page practice typing">
      <header className="typing-top">
        <button className="btn btn-ghost" onClick={onExit}>
          结束
        </button>
        <AmbiencePicker />
        <div className="learn-progress">
          <span style={{ width: `${(i / entries.length) * 100}%` }} />
        </div>
        <span className="typing-meter">
          <b>{m.wpm}</b> WPM · <b>{m.accuracy}%</b>
        </span>
      </header>
      <section
        className="typing-stage"
        onClick={(ev) => {
          if ((ev.target as HTMLElement).closest("button")) return;
          input.current?.focus();
          snapCaret();
        }}
      >
        {mode === "word" && (
          <div className="typing-cue">
            <Illustration src={atlas.img(e)} word={e.w} topic={0} eager />
            <p>
              <span className="pos">{e.senses[0].pos}</span> {e.senses[0].zh}
            </p>
          </div>
        )}
        {mode === "dictation" && (
          <div className="typing-actions">
            <button
              type="button"
              className="link typing-replay"
              onPointerDown={(ev) => pressControl(ev, replay)}
              onClick={(ev) => {
                ev.preventDefault();
                ev.stopPropagation();
                if (ev.detail === 0) replay();
              }}
            >
              再听一遍
            </button>
            <button
              type="button"
              className="link typing-reveal"
              aria-expanded={revealed}
              aria-controls="dictation-answer"
              onPointerDown={(ev) => pressControl(ev, reveal)}
              onClick={(ev) => {
                ev.preventDefault();
                ev.stopPropagation();
                if (ev.detail === 0) reveal();
              }}
            >
              看答案
            </button>
          </div>
        )}
        {mode === "dictation" && voiceNote && (
          <p className="typing-voice-note" role="status">
            {voiceNote}
          </p>
        )}
        {mode !== "word" && <p className="typing-zh">{e.ex[0].zh}</p>}
        {mode === "dictation" && revealed && (
          <div className="typing-compare" id="dictation-answer" role="region" aria-label="答案对照">
            <article>
              <span className="eyebrow">你的输入</span>
              <p lang="en">{value ? value : "（还没有输入）"}</p>
            </article>
            <article className="is-key">
              <span className="eyebrow">正确答案</span>
              <p lang="en">{target}</p>
            </article>
          </div>
        )}
        <p className={`typing-text ${mode === "word" ? "is-word" : ""} ${mode === "dictation" ? "is-hidden" : ""}`} lang="en" aria-hidden="true">
          {chars.map((ch, k) => {
            const t = typed[k];
            const slot = slots[k];
            const cls = slot === "empty" ? (k === typed.length ? "is-caret" : "") : slot === "ok" ? "is-ok" : "is-bad";
            const masked = mode === "dictation" && slot === "empty";
            const show = masked ? (ch === " " ? " " : /[A-Za-z]/.test(ch) ? "·" : ch) : slot === "bad" && t ? t : ch;
            return (
              <span key={k} className={cls}>
                {show}
              </span>
            );
          })}
        </p>
        <input
          ref={input}
          className="typing-input"
          value={value}
          onChange={(ev) => {
            const raw = ev.target.value;
            if (skipRaw.current !== null) {
              const skipped = skipRaw.current;
              skipRaw.current = null;
              if (skipped === raw) return;
            }
            onChange(raw);
          }}
          onCompositionStart={() => {
            composing.current = true;
            beforeComposition.current = valueRef.current;
          }}
          onCompositionEnd={(ev) => {
            const raw = ev.currentTarget.value;
            composing.current = false;
            skipRaw.current = raw;
            valueRef.current = beforeComposition.current;
            onChange(raw);
          }}
          onSelect={snapCaret}
          onFocus={snapCaret}
          autoFocus
          autoCapitalize="none"
          autoCorrect="off"
          autoComplete="off"
          spellCheck={false}
          enterKeyHint="done"
          aria-label="在这里输入"
        />
        <p className="muted typing-help">
          {mode === "dictation" ? "听不清可以点「再听一遍」。对一下可以点「看答案」，看过仍要自己打对才会进入下一句。" : "直接开始输入，全部正确后自动进入下一项。"} 第 {i + 1}/{entries.length} 项
        </p>
      </section>
    </div>
  );
}
