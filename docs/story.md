# Plot Twist — Story Design

Story decisions for the tennis mystery. This document describes *what* happens.
It is not code and not the story data file. Requirements come from
`docs/product-brief.md` (BRD); references like PT R3 point there.

## Premise

The player competes in a tennis tournament with a group stage. In round 2 the
string of their racket breaks. The tournament has no spare racket, so the
player has to find one. The groundskeeper has the key to an old equipment shed
where two rackets are stored. The choice between them decides the tournament.

**Plot twist:** the worn-out racket once belonged to "Roger F." The full name is
never mentioned.

## Scenes (story order)

| #   | Scene / location                | What happens |
| --- | ------------------------------- | ------------ |
| 1   | Tournament grounds              | Start of the game. |
| 2   | Tournament office (1st visit)   | The player registers. |
| 3   | Locker room                     | The player changes. |
| 4   | Court — round 1                 | Match with the original racket. Always won. |
| 5   | Court — round 2                 | Very hard match. The string breaks on the last point. Always lost. Because of the group stage, the player is still in the tournament (the text explains this). |
| 6   | Tournament office (2nd visit)   | The player asks for a spare racket. No spare is available. The office says the groundskeeper may know more. |
| 7   | Groundskeeper (next to a court) | Only appears after scene 6. Talking to him: he points to the old shed and hands over the **key**. |
| 8   | Equipment shed (corner of the grounds) | Locked until the player has the key. Inside are two rackets. Inspecting is optional. The player takes exactly one. |
| 9   | Court — rounds 3 and 4 (final)  | The result depends on the chosen racket (see match system). |
| 10a | Award ceremony — win            | The player receives the trophy, followed by the bonus scene. |
| 10b | Award ceremony — loss           | The player stands on the second step of the podium and applauds the winner. **Ending B.** |
| 11  | Bonus scene (after 10a)         | Text and animation only, no interaction. A mysterious person asks to look at the racket, grins, says *"You made a good choice, kid."* and disappears. It is only hinted that this is Roger F. **Ending A.** |

## Items

| Item           | Where                 | Notes |
| -------------- | --------------------- | ----- |
| Key            | Groundskeeper         | Collected once. Stays in the inventory after use (PT R2). |
| Wilson Blade   | Shed                  | Almost new, little wear. Inspecting it makes it look like the right choice. |
| Old Yonex      | Shed                  | Model unknown, heavily worn. Inspecting it reveals the faded letters "Roger F." on the side. |

- Only **one** racket can be taken. The choice is final: the other racket
  disappears, and the shed is empty afterwards.
- Right after the choice, a message says the player must hurry because the next
  match starts soon.
- Inspecting is optional and is **not** remembered.

## Conditions and remembered changes

| Condition                          | Set when                              | Effect |
| ---------------------------------- | ------------------------------------- | ------ |
| Knows about the groundskeeper      | 2nd visit to the tournament office    | The groundskeeper appears next to the court. |
| Has key                            | Groundskeeper hands over the key      | The shed can be unlocked. |
| Chosen racket (Wilson / Yonex)     | Taking a racket in the shed           | Decides rounds 3–4 and the ending. This is the consequential decision (PT04). |
| Match results (rounds 1–4)         | After each match                      | Story progress. |

### Locked shed (PT04, A1)

The shed is **visible** from the start. Without the key, trying to open it is
rejected with a message, and the player's location and inventory do not change.
With the key, the same interaction gets one extra option: unlock the shed.
After the first unlock, the shed stays open: the padlock lies in the grass and
the door leads straight inside.

### Groundskeeper dialogue (PT R3)

| State                            | He says |
| -------------------------------- | ------- |
| Before handing over the key      | Points to the shed and hands over the key. |
| Key handed over, no racket yet   | "There should still be spare rackets in the shed." |
| After the racket choice          | "So, did you find a racket?" (at the edge of the court, without a scene change) |

There is never a second key. People in the picture speak in speech bubbles;
narration appears in the text box.

## World map

Since `specs/bigger-world.md`, the grounds are split into five outdoor screens.
The story order and the rules stay the same; only where they happen changes.

```
                       [Center Court] ──▶ [Court 2]
                             ▲              (groundskeeper)
                             │
 [Entrance] ──▶ [Main path] ─┘
  (office)      (locker room, fountain)
                     │
                     ▼
              [Back corner]
                (shed)
```

- The steward stands at the entrance gate and stops the player before
  registration.
- The groundskeeper appears on Court 2 after the hint from the office.
- New approved texts: entrance after registration ("The entrance gate. The
  tournament office is right here, and the main path leads further into the
  grounds.") and Court 2 without the groundskeeper ("Court 2, a smaller court
  next to the Center Court. Nobody is playing here right now.").

## Access rules

| Phase                         | Accessible locations |
| ----------------------------- | -------------------- |
| Before registration           | Tournament grounds, tournament office. Courts and locker room are not accessible yet. |
| After registration            | Locker room. The courts are accessible only after changing in the locker room. |
| After leaving the locker room | Tournament office, shed, courts and the area around them, at any time. The locker room can **not** be entered again because the tournament has started. |

- **Blocked locations are always visible.** Trying to enter one shows a short
  message explaining why (e.g. the locker room after the tournament has
  started). The player's location and inventory do not change (PT R1).
- **Shed:** before the racket choice, both rackets are inside. After the choice,
  the shed is empty.
- **Starting a match:** a match is started at the net of the court with a
  "Start match" button. A match can only be started when one is due. An
  indicator at the net shows when that is the case. In stage 1 (text and
  buttons), the button is offered only when a match is due.

## Match system

The result of every round is **fixed by the story**. The minigame only shapes
how the match feels and can never change the result.

| Round     | Racket            | Difficulty                                   | Result |
| --------- | ----------------- | -------------------------------------------- | ------ |
| 1         | Original          | Easy                                         | Win |
| 2         | Original          | Extremely hard. The string breaks on the last point. | Loss (always) |
| 3         | Wilson            | Normal                                       | Win |
| 4 (final) | Wilson            | Extremely hard                               | Loss, leads to Ending B |
| 3         | Yonex             | Extremely hard at first, then easy           | Narrow win |
| 4 (final) | Yonex             | Overpowered, almost impossible to lose       | Win, leads to Ending A |

**Losing a round that should be a win:** the player chooses between

- **Replay match**: the same round starts again, and nothing else changes.
- **Give up**: a full new game. This is not an ending, and it asks for
  confirmation first (PT01).

**Winning a round that should be a loss:** on the last point, the screen goes
dark and a text says the ball hit the player on the temple at full force, they
passed out, and therefore lost the match. In round 2 the breaking string has
the same role.

## Endings

| Ending | Condition     | Content |
| ------ | ------------- | ------- |
| A      | Yonex chosen  | Tournament won: trophy, then the bonus scene with the mysterious person. |
| B      | Wilson chosen | Final lost: the player applauds the winner at the ceremony. |

Once an ending is reached, ordinary story actions stop. The player can review
the outcome or start a new game (PT05).

## Save and resume

- Progress is saved after each accepted action.
- When the app is reopened, the game resumes where it was: scene, items,
  racket choice, conditions, and match results.
- If the app was closed **during a match**, the game resumes at the start of
  that match. Points within a match are not saved.
- A new game (or "Give up") asks for confirmation, then resets all progress.

## Approved texts

Final wording, approved by the author. The story data file uses these texts.

### Tournament grounds

- **Start:**
  > Sunshine, the pop of tennis balls, and a crowd finding their seats. Your name
  > is on the draw. Now you just need to register at the tournament office.
- **Later (free to explore):**
  > The courts are busy and the crowd is buzzing. The tournament office is by the
  > entrance, and an old shed sits in the corner of the grounds.

### Scene descriptions

- **Tournament office:**
  > A small office by the entrance. A woman sits behind a desk covered in draw
  > sheets.
- **Locker room:**
  > Rows of lockers and a wooden bench. It smells of fresh towels.
- **Courts, match due:**
  > The umpire waves you over to the net. Your next match is ready.
- **Courts, quiet, groundskeeper known:**
  > The court is quiet for now. Next to it, the groundskeeper is raking the clay.
- **Courts, quiet:**
  > The court is quiet for now.
- **Groundskeeper:**
  > The groundskeeper is raking the clay next to the court.

### Tournament office (1st visit, registration)

> "Name?" The woman at the desk runs her finger down a list. "There you are."
> She hands you a player badge. "The group stage starts soon. You can get
> changed in the locker room."

### Tournament office (later visits)

- **No racket yet:**
  > "Did you find the groundskeeper? He's usually somewhere by the courts."
- **After the racket choice:**
  > "Good luck out there!"

### Locker room

> You change into your tennis kit and check your racket one last time. The
> strings feel good. Time to play.

### Tournament office (2nd visit)

> The woman at the desk shakes her head. "A broken string? I'm sorry, we gave
> out our last spare racket this morning." She thinks for a moment. "Ask the
> groundskeeper. He's usually somewhere by the courts. If anyone knows where to
> find a racket, it's him."

### Groundskeeper

- **Before handing over the key:**
  > The groundskeeper leans on his rake and listens. "Broken string in the group
  > stage? Bad luck, buddy." He digs into his pocket and holds out a rusty key.
  > "There's an old shed in the corner of the grounds. There should still be a
  > few rackets in there."
- **Key handed over, no racket yet:**
  > "There should still be spare rackets in the shed."
- **After the racket choice:**
  > "So, did you find a racket?"

### Shed

- **Locked (description):**
  > An old wooden shed in the corner of the grounds. The paint is peeling, and a
  > heavy padlock hangs on the door.
- **Open without key (rejected):**
  > You pull at the door, but the padlock won't budge. You'll need a key.
- **Open (after the first unlock):**
  > An old wooden shed in the corner of the grounds. The padlock lies in the
  > grass, and the door stands ajar.
- **Unlocked, with rackets:**
  > The lock clicks open and the door creaks. Dust floats in the light. Between
  > old nets and ball baskets, two rackets lean against the wall. One looks
  > almost new. The other has clearly seen better days.
- **Empty (after the choice):**
  > The shed is empty now. Just old nets, ball baskets and dust.

### Inspecting

- **Wilson Blade:**
  > A Wilson Blade. The grip is clean, the strings are tight, and there's barely
  > a scratch on the frame. It looks almost new. This could be exactly what you
  > need.
- **Old Yonex:**
  > An old Yonex. The paint is chipped, the grip is worn thin, and the model name
  > has faded completely. It doesn't look like much. You turn it in your hands,
  > and on the side of the frame, barely readable, you make out two faded words:
  > *Roger F.*

### After the racket choice

> You take the racket. A voice crackles over the loudspeaker: "Next match
> starting soon!" You'd better hurry back to the courts.

### Blocked locations

- **Courts or locker room before registration:**
  > A steward stops you. "Sorry, players only. Please register at the tournament
  > office first."
- **Courts before changing:**
  > You're still in your street clothes. Get changed in the locker room first.
- **Locker room after the tournament has started:**
  > The locker room is closed. The tournament has already started.
- **Shed before changing:**
  > Not now. Get changed first, your first match starts soon.

### Matches

- **Round 1 (win):**
  > You find your rhythm quickly. Clean serves, deep returns. Match won!
- **Round 2 (string breaks):**
  > Your opponent is relentless. On the very last point you swing hard and hear a
  > sharp *ping*. Your string has snapped, and the ball floats into the net.
  > Match lost.
- **Group stage line (right after round 2):**
  > Thanks to your win in round 1, you're still in the tournament. But you can't
  > play the next match without a racket.
- **Round 3, Wilson (win):**
  > The Wilson feels light and fast in your hand. It isn't easy, but you win the
  > match. Next up: the final.
- **Round 3, Yonex (narrow win):**
  > The first points are a disaster. The old racket feels strange in your hand.
  > But slowly, something clicks. You win, just barely. Next up: the final.
- **Final, Wilson (loss):**
  > In the final, nothing works. Your shots land long and your serve lets you
  > down. You lose the final.
- **Final, Yonex (win):**
  > Every shot lands exactly where you want it. Your opponent has no answer. You
  > win the final!
- **Blackout (winning a round that must be lost):**
  > On the last point, the ball hits you on the temple at full force. Everything
  > goes dark. When you wake up, the match is over. You lost.
- **Losing a round that must be won:**
  > That one slipped away. Do you want to replay the match or give up?

  Buttons: **Replay match** / **Give up**
- **Give up, confirmation:**
  > Giving up starts a completely new game. All your progress will be lost. Are
  > you sure?

### Award ceremony and endings

- **Win:**
  > Confetti rains down as you lift the trophy. The crowd cheers your name.
- **Bonus scene, then Ending A:**
  > As the crowd drifts away, a stranger in a cap walks up to you. "May I take a
  > look at that racket?" He turns it slowly in his hands, his thumb resting on
  > the faded letters on the frame. A smile spreads across his face. "You made a
  > good choice, kid." He hands it back, and before you can say a word, he's
  > gone.
  >
  > **ENDING A: The Racket of a Legend**
- **Loss, Ending B:**
  > You stand on the second step as the winner lifts the trophy, clapping along
  > with the crowd. So close.
  >
  > **ENDING B: Runner-up**

### New game confirmation (PT01)

> Start a new game? Your current progress will be replaced.

Buttons: **Yes, start over** / **Cancel**

## Delivery stages

1. **Core:** scenes, items, rules, and saving with text and buttons. Covers the
   BRD and scenarios A1–A6. The first feature (`first-feature`) is part of this
   stage.
2. **Match minigame:** a browser-based timing game that only reports win or loss
   back to Python.
3. **World map:** a top-down 2D map of the grounds in a simple block style,
   where the player can walk around freely. It triggers the same actions as the
   buttons, and the buttons stay as a fallback.

## Notes

- Possible extension after stage 2: depending on how the minigame feels, add
  another round so there is more to play. The number of rounds must therefore
  come from the story data and must not be hard-coded in `logic.py`. The ending
  follows the result of the last round.

- In stage 1, the "Start match" button applies the fixed result directly. The
  minigame replaces this in stage 2.
