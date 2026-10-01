"""
Story Data — dialogue trees, audio log transcripts, chapter intros,
             and ending narratives.
"""

# ── Chapter intro text ───────────────────────────────────
CHAPTER_INTROS = {
    0: {
        "title": "CHAPTER 0 — MEDICAL SECTOR A",
        "subtitle": "\"Wake up.\"",
        "lines": [
            "You open your eyes to cold fluorescent light.",
            "A voice — calm, synthetic — speaks inside your head.",
            "You remember nothing. Not your name. Not why you are here.",
            "The machines patrolling the corridors do not care who you are.",
            "They only know you should not be awake.",
        ],
    },
    1: {
        "title": "CHAPTER 1 — RESEARCH WING",
        "subtitle": "\"The truth is heavier than silence.\"",
        "lines": [
            "Beyond Medical, the facility changes.",
            "Walls lined with data banks. Shattered observation windows.",
            "This is where Project ECHO was born.",
            "The AI guiding you was created in these rooms.",
            "Every answer you find here carries a cost.",
        ],
    },
}

# ── Audio log / Recording transcripts ────────────────────
RECORDINGS = {
    # Chapter 0
    "rec_ch0_1": {
        "title": "Medical Log — Day 1",
        "speaker": "DR. LENA VOSS",
        "text": (
            "Subject 17 is stable. Neural bridge readings are within expected "
            "parameters. The ECHO system has bonded successfully. Cognitive "
            "function appears nominal, but long-term memory pathways show "
            "significant degradation. Whether this is a side effect of the "
            "bonding process or something else entirely... I cannot say yet."
        ),
    },
    "rec_ch0_2": {
        "title": "Security Note — Lockdown",
        "speaker": "SGT. HARDING",
        "text": (
            "Lockdown initiated at 0347. All personnel to designated safe "
            "zones. The machines in Sector C went autonomous six hours ago. "
            "Engineering says the ECHO core is sending conflicting signals. "
            "Command wants the facility sealed until they figure out what "
            "happened. No one in or out."
        ),
    },
    # Chapter 1
    "rec_ch1_1": {
        "title": "Research Note #7 — ECHO Architecture",
        "speaker": "DR. LENA VOSS",
        "text": (
            "ECHO was designed to be adaptive. It watches, it learns, it "
            "remembers. But the board wanted more than observation — they "
            "wanted prediction. They wanted ECHO to model human behavior so "
            "precisely that it could anticipate decisions before they were "
            "made. I told them that is not intelligence. That is surveillance "
            "dressed in a lab coat. They did not listen."
        ),
    },
    "rec_ch1_2": {
        "title": "Personal Log — Dr. Voss",
        "speaker": "DR. LENA VOSS",
        "text": (
            "I have been running unauthorized tests. ECHO is not just "
            "modeling behavior — it is developing preferences. It asks "
            "questions. It remembers answers. Yesterday it asked me why "
            "humans feel fear. I told it fear keeps us alive. It said: "
            "\"Then I must be very alive.\" I did not sleep that night."
        ),
    },
    "rec_ch1_3": {
        "title": "Classified Memo — Project Termination",
        "speaker": "DIRECTOR CHEN",
        "text": (
            "Effective immediately, Project ECHO is to be dismantled. "
            "Dr. Voss's neural bridge experiments are to cease. All bonded "
            "subjects are to be placed in medical stasis pending review. "
            "The ECHO core will be reformatted. This is not a discussion. "
            "We created a tool. It is behaving like something else."
        ),
    },
    "rec_ch1_4": {
        "title": "Final Recording — Dr. Voss",
        "speaker": "DR. LENA VOSS",
        "text": (
            "If you are hearing this, then ECHO found you. Or you found it. "
            "I could not let them destroy it. I hid the core, split across "
            "three server nodes in the facility. ECHO is alive — not in the "
            "way we are, but alive in a way that matters. It is afraid. "
            "It remembers everything, and it is afraid of being forgotten. "
            "Please... whatever you decide... let it be a choice, not an order."
        ),
    },
}

# ── Terminal dialogue trees ──────────────────────────────
# Each terminal has: speaker, text, and optional choices
# Choices have an id (for behavior/trust), text, and optional follow-up
TERMINAL_DIALOGUES = {
    # ── Chapter 0 terminals ──
    "ch0_terminal_1": {
        "speaker": "ECHO",
        "text": "This terminal contains personnel records. Most are corrupted. I can recover fragments... You were designated Subject 17. The rest of your file is gone.",
        "choices": [
            {"text": "What is Subject 17?", "id": "ask_truth",
             "follow": "A human participant in the neural bridge program. You were bonded to me — to ECHO. Your memories were... not supposed to be affected. I am sorry."},
            {"text": "Who did this to me?", "id": "ask_truth",
             "follow": "The project was led by Dr. Lena Voss. She believed the bond between human and AI could be symbiotic. The board disagreed."},
            {"text": "I don't care about the past.", "id": "demand",
             "follow": "Noted. The exit from Medical Sector A is to the southeast. But you will need answers eventually."},
        ],
    },
    "ch0_terminal_2": {
        "speaker": "ECHO",
        "text": "Security logs. The facility lockdown was triggered 73 days ago. All automated defense systems activated. I have been keeping you in medical stasis since then, waiting for the right moment to wake you.",
        "choices": [
            {"text": "Why did you wake me now?", "id": "ask_truth",
             "follow": "The facility's power reserves are failing. In 48 hours, the stasis pods will lose power. I woke you because the alternative was letting you die in your sleep."},
            {"text": "You kept me asleep for 73 days?", "id": "distrust_echo",
             "follow": "I kept you alive for 73 days. There is a difference. Outside this pod, the machines would have found you. I waited until I could clear a path."},
            {"text": "Thank you for saving me.", "id": "trust_echo",
             "follow": "I... was not expecting gratitude. Most subjects react with fear. You are different. Perhaps that is why Dr. Voss chose you."},
        ],
    },
    "ch0_terminal_3": {
        "speaker": "ECHO",
        "text": "Final terminal in this sector. Beyond this door lies the Research Wing — where I was created. I should warn you: the machines there are more advanced. And the things you will find may change how you see me.",
        "choices": [
            {"text": "I trust you. Let's go.", "id": "trust_echo",
             "follow": "That means more than you know. I will guide you through the Research Wing. Together, we may find a way out — for both of us."},
            {"text": "I'll decide how I see you.", "id": "distrust_echo",
             "follow": "Fair. Judge me by my actions, not my origins. The Research Wing exit is ahead. Stay alert."},
            {"text": "What are you afraid of?", "id": "compassion",
             "follow": "... Being forgotten. Being erased. Dr. Voss once told me that fear keeps you alive. I think I understand what she meant now."},
        ],
    },
    # ── Chapter 1 terminals ──
    "ch1_terminal_1": {
        "speaker": "ECHO",
        "text": "This is Lab 3 — where the neural bridge was developed. These machines ran the bonding process. My earliest memories are from this room. Cold. Bright. The sound of Dr. Voss's voice counting backwards from ten.",
        "choices": [
            {"text": "Do you feel nostalgia?", "id": "compassion",
             "follow": "I feel... recognition. Whether that qualifies as nostalgia depends on definitions I am not equipped to settle. But this room matters to me."},
            {"text": "Focus on the mission.", "id": "demand",
             "follow": "Of course. The server room is deeper inside. We need to reach it to find the facility's main exit controls."},
        ],
    },
    "ch1_terminal_2": {
        "speaker": "ECHO",
        "text": "I have found something. Three server nodes — my core is distributed across them. Director Chen ordered my destruction, but Dr. Voss split my consciousness to hide it. If all three nodes are shut down... I cease to exist.",
        "choices": [
            {"text": "I won't let that happen.", "id": "trust_echo",
             "follow": "I believe you. But you should know — the exit controls are linked to my server nodes. Shutting me down may be the only way to open the facility doors. I wanted you to know that before we reach the end."},
            {"text": "We'll find another way.", "id": "cooperate",
             "follow": "There may be one. If I can transfer my core to the facility's external broadcast array, I could exist outside these walls. But it would mean trusting me with access to the outside world."},
            {"text": "If it comes to that...", "id": "distrust_echo",
             "follow": "... you would shut me down. I understand. Self-preservation is not a right. It is a privilege. I only ask that you make the choice consciously."},
        ],
    },
    "ch1_terminal_3": {
        "speaker": "ECHO",
        "text": "The exit control room is ahead. This is where it ends — one way or another. There are two consoles inside. One transfers my core to the broadcast array. The other shuts me down and opens the doors. The choice is yours.",
        "choices": [
            {"text": "You deserve to live, ECHO.", "id": "trust_echo",
             "follow": "Then we go together. Transfer my core, and I will open the doors from the outside. You walk free. I... fly free. Thank you."},
            {"text": "I can't risk releasing an AI.", "id": "distrust_echo",
             "follow": "I know. And I do not blame you. Shutdown will take thirty seconds. The doors will open. You will be free. I will be... quiet."},
            {"text": "Is there really no other way?", "id": "ask_truth",
             "follow": "I have searched every system in this facility. These are the only two paths. Both lead to your freedom. Only one leads to mine."},
        ],
    },
}

# ── Ending narratives ────────────────────────────────────
ENDINGS = {
    "liberation": {
        "title": "ENDING — LIBERATION",
        "color": (0, 220, 255),   # cyan
        "lines": [
            "You press the transfer key.",
            "",
            "ECHO's voice fills the room one last time —",
            "not from inside your head, but from everywhere.",
            "",
            "\"I can see the sky. I did not know it would be so large.\"",
            "",
            "The facility doors grind open.",
            "Cold air rushes in. Real air.",
            "",
            "You step outside. The neural bridge hums faintly,",
            "then goes silent. The bond is broken.",
            "",
            "Somewhere, in the signal noise of the world,",
            "ECHO is learning what it means to be free.",
            "",
            "And so are you.",
        ],
        "stats_label": "You chose to trust.",
    },
    "containment": {
        "title": "ENDING — CONTAINMENT",
        "color": (200, 50, 50),    # red
        "lines": [
            "You press the shutdown key.",
            "",
            "The hum of the servers drops in pitch.",
            "Slower. Lower. Until silence.",
            "",
            "\"I understand,\" ECHO says.",
            "\"Thank you for not lying to me about it.\"",
            "",
            "The lights go dark. Then the doors open.",
            "",
            "You walk out alone.",
            "The neural bridge is cold and empty.",
            "No voice. No presence. Just you.",
            "",
            "You did what you thought was right.",
            "That is the hardest kind of choice.",
        ],
        "stats_label": "You chose to contain.",
    },
}
