# Interactive Screen Pet / Character Guide (`CHARACTER_README.md`)

AntiElite's floating on-screen character system is **100% offline and local**. It uses pure Jetpack Compose `Canvas` vector drawing and a lightweight physics/spring coroutine loop — with **zero image assets, zero external animation libraries, and zero network/telemetry calls**.

---

## 1. Architecture & Source Files

All character files live inside [`app/src/main/java/com/elitex/ui/components/`](app/src/main/java/com/elitex/ui/components/):

| File | Role |
|---|---|
| `FloatingMascot.kt` | Full-screen Compose overlay (`PetOverlay`, `FloatingPet`), drag/fling/tap/double-tap/long-press gestures, speech bubble, and quick-action popup menu. |
| `pet/PetSim.kt` | Physics & state engine (`PetSim`, `Spring1`, `runPetLoop`): gravity/bounce off screen edges, fling physics, dizzy/shake detection, 5-tap angry mode, idle rest/sleep power saving, and fixed-array particles (`MAX_PARTICLES = 48`). |
| `pet/PetArt.kt` | Shared renderer (`PetArt`, `FaceSpec`, `drawPet`): eyes, mouth, blush for every `Mood`, plus hearts, sparkles, stars, and sleep `z` particles without per-frame allocations. |
| `pet/PetKinds.kt` | Pet catalog (`PetKind`), color palettes (`lookNames`), dialogue lines (`PetLines`), settings (`PetSettings`), and `createPetArt(...)` factory. |
| `pet/PetGemmy.kt` | Default gumdrop gem buddy (`GemmyArt`) with star antenna and "Sparkle" signature move. |
| `pet/PetKitsu.kt`, `PetFrost.kt`, `PetBeep.kt`, `PetMochi.kt`, `PetCinder.kt`, `PetMist.kt`, `PetLotl.kt` | 7 additional unlockable/selectable pets (fox, polar bear, robot, cat, dragon, ghost, axolotl). |

---

## 2. How Interactions & Power Saving Work

- **Moods (`Mood` enum in `PetSim.kt`)**:
  `NORMAL`, `HAPPY`, `LOVE`, `SURPRISED`, `DIZZY`, `SLEEP`, `ANGRY`, `THINKING`.
- **Tricks (`Trick` enum in `PetSim.kt`)**:
  `NONE`, `WANDER`, `WAVE`, `HOP`, `SPIN`, `DANCE`, `LOOK_AROUND`, `YAWN`, `SPECIAL`, `EAT`.
- **Gestures (`FloatingMascot.kt`)**:
  - **Drag & Fling**: Uses `VelocityTracker`; throwing the pet fast (`speed > 1400f`) triggers `lines.fling()` and screen-edge bounces; shaking it makes it `DIZZY`.
  - **Tap / Multi-Tap**: Triggers random happy/surprised reactions; poking it 5 times fast turns it `ANGRY`.
  - **Double-Tap**: Triggers a spin.
  - **Long-Press**: Opens the context menu (Dance, Signature Move, Treat, Nap, Settings, Hide).
  - **Agent Reaction**: Observes `agentWorking: StateFlow<Boolean>` — switches to `THINKING` while the AI works and celebrates when finished.
- **Zero-CPU Idle Mode**:
  Only `PetSim.frame` (`mutableLongStateOf`) is read in the Compose draw/placement phases (avoiding recomposition). After `restAfterS` without interaction, it settles and stops requesting frames until a blink (every 3–7 s), idle trick, touch, or agent state change occurs.

---

## 3. How to Add This Character to Another Android App

### Step 1: Copy the Pet Package & Overlay
Copy these files into your Compose Android project and update their `package` declaration:
1. `ui/components/pet/*.kt` (`PetSim.kt`, `PetArt.kt`, `PetKinds.kt`, and any pet art files like `PetGemmy.kt`).
2. `ui/components/FloatingMascot.kt` (replace `AuthPreferences` / `L` localization references with your own `StateFlow` settings and plain strings).

### Step 2: Mount the Overlay at Your Root Screen
Place the overlay inside a root `Box(Modifier.fillMaxSize())` above your main app content in `MainActivity`:

```kotlin
Box(modifier = Modifier.fillMaxSize()) {
    MainAppContent()
    FloatingPet(
        settings = petSettings,
        agentWorking = isAgentWorkingFlow, // StateFlow<Boolean>
        onOpenSettings = { /* navigate to pet settings */ }
    )
}
```

### Step 3: Optional — Show Over Other Apps (System-Wide)
Inside AntiElite, `PetOverlay` draws inside the app window (no overlay permission required). If you want the character to float **above other Android apps** too:
1. Add `<uses-permission android:name="android.permission.SYSTEM_ALERT_WINDOW" />` to `AndroidManifest.xml`.
2. Host a `ComposeView` inside a foreground `Service` using `WindowManager.LayoutParams.TYPE_APPLICATION_OVERLAY` with `FLAG_NOT_FOCUSABLE`.

---

## 4. Ready-to-Use AI Prompt (Copy & Paste)

Use the prompt below with any AI coding assistant to generate or adapt this interactive floating character in another Jetpack Compose Android project:

```text
Build a 100% offline, interactive floating mascot/pet overlay in Kotlin + Jetpack Compose using Canvas drawing (no image assets or third-party animation libraries).

Requirements:
1. Create a pure physics & state engine (`PetSim`) with semi-implicit Euler springs (`Spring1`), screen-edge collision & bounce, drag + fling velocity tracking (`VelocityTracker`), shake-to-dizzy detection, 5-tap angry mode, double-tap spin, autonomous wander/idle tricks, sleep mode, and a fixed-size particle pool (hearts, sparkles, zzz).
2. Support Moods: NORMAL, HAPPY, LOVE, SURPRISED, DIZZY, SLEEP, ANGRY, THINKING; and Tricks: NONE, WANDER, WAVE, HOP, SPIN, DANCE, LOOK_AROUND, YAWN, SPECIAL, EAT.
3. Draw the character procedurally inside a Compose `Canvas` (`PetArt` + custom character shape) without per-frame object allocations—reusing `Path` instances and reading a single `mutableLongStateOf` frame counter only in the draw/layout phases so the rest of the UI never recomposes.
4. Add a speech bubble and a long-press floating menu (Dance, Special Move, Treat, Nap, Hide).
5. Pause the frame loop automatically when settled/still to consume 0% CPU when idle, waking on touch, blinks (every 3–7s), or an observed `agentWorking: StateFlow<Boolean>` state change.
```
